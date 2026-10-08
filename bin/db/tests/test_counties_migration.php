<?php

/** Compare real migration columns with schema.sql in the dedicated scratch database only. */
declare(strict_types=1);

require dirname(__DIR__, 2).'/vendor/autoload.php';
require dirname(__DIR__).'/migrations/20261008000000_create_counties_table.php';

$pdo = new PDO('mysql:host=127.0.0.1;dbname=world_phase2b_fix;charset=utf8mb4', 'root', '', [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);
$pdo->exec(file_get_contents(dirname(__DIR__).'/schema.sql'));
$expected = $pdo->query('SHOW COLUMNS FROM counties')->fetchAll(PDO::FETCH_ASSOC);
$adapter = new Phinx\Db\Adapter\MysqlAdapter([
    'host' => '127.0.0.1', 'name' => 'world_phase2b_fix', 'user' => 'root', 'pass' => '',
    'port' => 3306, 'charset' => 'utf8mb4',
]);
$migration = new CreateCountiesTable('testing', 20261008000000);
$migration->setAdapter($adapter);
$migration->down();
$migration->up();
$actual = $pdo->query('SHOW COLUMNS FROM counties')->fetchAll(PDO::FETCH_ASSOC);
$failures = [];
foreach ($expected as $index => $column) {
    if (($actual[$index] ?? null) !== $column) {
        $failures[] = $column['Field'].': '.json_encode($actual[$index] ?? null).' != '.json_encode($column);
    }
}
if (count($actual) !== count($expected) || $failures) {
    throw new RuntimeException("Migration differs from schema.sql:\n".implode("\n", $failures));
}
echo 'County migration: all '.count($expected)." SHOW COLUMNS definitions match schema.sql\n";
