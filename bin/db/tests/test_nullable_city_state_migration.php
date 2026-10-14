<?php

/**
 * v5 cities without a state, on a dedicated scratch database (its name must end in _test; it is dropped first):
 * the fresh schema and the upgrade both allow a null pair and refuse a half one; a used state cannot be deleted;
 * rolling back is refused while a city has no state, and works once none has.
 * Run: php bin/db/tests/test_nullable_city_state_migration.php   (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, TEST_DB)
 */
declare(strict_types=1);

require dirname(__DIR__, 2).'/vendor/autoload.php';
require dirname(__DIR__).'/migrations/20261014000000_nullable_city_state.php';

$host = getenv('MYSQL_HOST') ?: '127.0.0.1';
$user = getenv('MYSQL_USER') ?: 'root';
$pass = getenv('MYSQL_PASSWORD') ?: '';
$db = getenv('TEST_DB') ?: 'csc_nullable_state_test';
if (!preg_match('/^[a-z0-9_]+_test$/', $db)) {
    throw new InvalidArgumentException("TEST_DB must be a scratch database whose name ends in _test, got {$db}");
}

$server = new PDO("mysql:host={$host};charset=utf8mb4", $user, $pass, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$server->exec("DROP DATABASE IF EXISTS `{$db}`");
$server->exec("CREATE DATABASE `{$db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
$pdo = new PDO("mysql:host={$host};dbname={$db};charset=utf8mb4", $user, $pass, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$pdo->exec(file_get_contents(dirname(__DIR__).'/schema.sql'));
$pdo->exec("INSERT INTO countries (id, name, iso2, iso3) VALUES (244, 'Western Sahara', 'EH', 'ESH'), (233, 'United States', 'US', 'USA')");
$pdo->exec("INSERT INTO states (id, name, country_id, country_code, iso2) VALUES (1457, 'Louisiana', 233, 'US', 'LA')");

$failures = [];
/** Record a failure unless the statement is refused with the expected MySQL error code. */
$refused = function (string $sql, int $code, string $what) use ($pdo, &$failures): void {
    try {
        $pdo->exec($sql);
        $failures[] = "{$what}: accepted";
    } catch (PDOException $e) {
        if ((int) ($e->errorInfo[1] ?? 0) !== $code) {
            $failures[] = "{$what}: error {$e->errorInfo[1]}, expected {$code}";
        }
    }
};
/** Whether both state columns allow NULL. */
$nullable = fn (): bool => count(array_filter(
    $pdo->query("SHOW COLUMNS FROM cities WHERE Field IN ('state_id', 'state_code')")->fetchAll(PDO::FETCH_ASSOC),
    fn ($c) => $c['Null'] === 'YES'
)) === 2;
$stateless = "INSERT INTO cities (id, name, state_id, state_code, country_id, country_code, latitude, longitude) VALUES (1, 'Smara', NULL, NULL, 244, 'EH', 26.7, -11.6)";
$halfNull = "INSERT INTO cities (id, name, state_id, state_code, country_id, country_code, latitude, longitude) VALUES (3, 'Bad', NULL, 'LA', 233, 'US', 30, -90)";
$halfNullCode = "INSERT INTO cities (id, name, state_id, state_code, country_id, country_code, latitude, longitude) VALUES (4, 'Bad', 1457, NULL, 233, 'US', 30, -90)";

// fresh schema
$pdo->exec($stateless);
$pdo->exec("INSERT INTO cities (id, name, state_id, state_code, country_id, country_code, latitude, longitude) VALUES (2, 'Baton Rouge', 1457, 'LA', 233, 'US', 30.4, -91.1)");
$refused($halfNull, 3819, 'fresh schema, half-null pair');
$refused($halfNullCode, 3819, 'fresh schema, state without its code');
$refused('DELETE FROM states WHERE id = 1457', 1451, 'deleting a state that a city uses');

// upgrade and rollback through the migration itself
$migration = new NullableCityState('testing', 20261014000000);
$migration->setAdapter(new Phinx\Db\Adapter\MysqlAdapter([
    'host' => $host, 'name' => $db, 'user' => $user, 'pass' => $pass, 'port' => 3306, 'charset' => 'utf8mb4',
]));
try {
    $migration->down();
    $failures[] = 'rollback with a stateless city: accepted';
} catch (RuntimeException $e) {
    // expected: a city has no state
}
$pdo->exec('DELETE FROM cities WHERE id = 1');
$migration->down();
if ($nullable()) {
    $failures[] = 'after rollback the state columns still allow NULL';
}
$refused($stateless, 1048, 'rolled back schema, stateless city');
$migration->up();
if (!$nullable()) {
    $failures[] = 'after upgrade the state columns do not allow NULL';
}
$pdo->exec($stateless);
$refused($halfNull, 3819, 'upgraded schema, half-null pair');
$refused($halfNullCode, 3819, 'upgraded schema, state without its code');

$server->exec("DROP DATABASE `{$db}`");
if ($failures) {
    throw new RuntimeException("Nullable city state:\n".implode("\n", $failures));
}
echo "Nullable city state: fresh schema, upgrade, refused and successful rollback all behave as documented\n";
