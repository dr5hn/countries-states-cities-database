<?php

/**
 * v5 counties of several regions, on a dedicated scratch database (its name must end in _test; it is dropped first):
 * the fresh schema and the upgrade allow a county with no state whose regions are county_states rows, refuse a half
 * pair, a repeated pair or an unknown state, and cascade a removed county's rows; rolling back is refused while a
 * county has no state or a relation row exists, and works once none does.
 * Run: php bin/db/tests/test_county_states_migration.php   (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, TEST_DB)
 */
declare(strict_types=1);

require dirname(__DIR__, 2).'/vendor/autoload.php';
require dirname(__DIR__).'/migrations/20261015000000_county_states.php';

$host = getenv('MYSQL_HOST') ?: '127.0.0.1';
$user = getenv('MYSQL_USER') ?: 'root';
$pass = getenv('MYSQL_PASSWORD') ?: '';
$db = getenv('TEST_DB') ?: 'csc_county_states_test';
if (!preg_match('/^[a-z0-9_]+_test$/', $db)) {
    throw new InvalidArgumentException("TEST_DB must be a scratch database whose name ends in _test, got {$db}");
}

$server = new PDO("mysql:host={$host};charset=utf8mb4", $user, $pass, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$server->exec("DROP DATABASE IF EXISTS `{$db}`");
$server->exec("CREATE DATABASE `{$db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
$pdo = new PDO("mysql:host={$host};dbname={$db};charset=utf8mb4", $user, $pass, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
$pdo->exec(file_get_contents(dirname(__DIR__).'/schema.sql'));
$pdo->exec("INSERT INTO countries (id, name, iso2, iso3) VALUES (158, 'New Zealand', 'NZ', 'NZL')");
$pdo->exec("INSERT INTO states (id, name, country_id, country_code, iso2) VALUES (4060, 'Manawatu-Whanganui', 158, 'NZ', 'MWT'), " .
    "(4061, 'Waikato', 158, 'NZ', 'WKO')");

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
/** Whether both county state columns allow NULL. */
$nullable = fn (): bool => count(array_filter(
    $pdo->query("SHOW COLUMNS FROM counties WHERE Field IN ('state_id', 'state_code')")->fetchAll(PDO::FETCH_ASSOC),
    fn ($c) => $c['Null'] === 'YES'
)) === 2;
/** Whether the county_states table exists. */
$relation = fn (): bool => (bool) $pdo->query("SHOW TABLES LIKE 'county_states'")->fetch();
$severalRegions = "INSERT INTO counties (id, name, state_id, state_code, country_id, country_code, latitude, longitude) " .
    "VALUES (9, 'Waitomo District', NULL, NULL, 158, 'NZ', -38.35, 175.18333333)";
$links = 'INSERT INTO county_states (county_id, state_id) VALUES (9, 4060), (9, 4061)';
$halfNull = "INSERT INTO counties (id, name, state_id, state_code, country_id, country_code, latitude, longitude) " .
    "VALUES (3, 'Bad', NULL, 'WKO', 158, 'NZ', -38, 175)";
$halfNullCode = "INSERT INTO counties (id, name, state_id, state_code, country_id, country_code, latitude, longitude) " .
    "VALUES (4, 'Bad', 4061, NULL, 158, 'NZ', -38, 175)";

/** The checks that hold on any schema with the migration applied. */
$checkMigrated = function (string $where) use ($pdo, $refused, $severalRegions, $links, $halfNull, $halfNullCode, &$failures): void {
    $pdo->exec($severalRegions);
    $pdo->exec($links);
    $refused($halfNull, 3819, "{$where}, half-null county pair");
    $refused($halfNullCode, 3819, "{$where}, county state without its code");
    $refused('INSERT INTO county_states (county_id, state_id) VALUES (9, 4060)', 1062, "{$where}, repeated region");
    $refused('INSERT INTO county_states (county_id, state_id) VALUES (9, 99)', 1452, "{$where}, unknown state");
    $refused('INSERT INTO county_states (county_id, state_id) VALUES (77, 4060)', 1452, "{$where}, unknown county");
    $refused('DELETE FROM states WHERE id = 4060', 1451, "{$where}, deleting a region a county lists");
    $pdo->exec('DELETE FROM counties WHERE id = 9');
    if ((int) $pdo->query('SELECT COUNT(*) FROM county_states')->fetchColumn() !== 0) {
        $failures[] = "{$where}: removing the county left its region rows";
    }
};

// fresh schema
$checkMigrated('fresh schema');

// upgrade and rollback through the migration itself
$migration = new CountyStates('testing', 20261015000000);
$migration->setAdapter(new Phinx\Db\Adapter\MysqlAdapter([
    'host' => $host, 'name' => $db, 'user' => $user, 'pass' => $pass, 'port' => 3306, 'charset' => 'utf8mb4',
]));
$pdo->exec($severalRegions);
$pdo->exec($links);
try {
    $migration->down();
    $failures[] = 'rollback with a county of several regions: accepted';
} catch (RuntimeException $e) {
    // expected: a county has no state
}
$pdo->exec('DELETE FROM counties WHERE id = 9');
$migration->down();
if ($nullable() || $relation()) {
    $failures[] = 'after rollback the county state still allows NULL or county_states remains';
}
$refused($severalRegions, 1048, 'rolled back schema, county with no state');
$migration->up();
if (!$nullable() || !$relation()) {
    $failures[] = 'after upgrade the county state does not allow NULL or county_states is missing';
}
$checkMigrated('upgraded schema');

$server->exec("DROP DATABASE `{$db}`");
if ($failures) {
    throw new RuntimeException("County states:\n".implode("\n", $failures));
}
echo "County states: fresh schema, upgrade, refused and successful rollback all behave as documented\n";
