<?php

declare(strict_types=1);

use Phinx\Migration\AbstractMigration;
use Phinx\Db\Adapter\MysqlAdapter;

/** Adds intermediate administrative units and optional city county links (#1303). */
final class CreateCountiesTable extends AbstractMigration
{
    /** Create counties before adding the dependent city foreign key. */
    public function up(): void
    {
        if (!$this->hasTable('counties')) {
            $table = $this->table('counties', [
                'id' => false, 'primary_key' => ['id'],
                'engine' => 'InnoDB', 'collation' => 'utf8mb4_unicode_ci',
            ]);
            $mediumInt = ['signed' => false, 'limit' => MysqlAdapter::INT_MEDIUM];
            $table->addColumn('id', 'integer', $mediumInt + ['identity' => true, 'null' => false])
                ->addColumn('name', 'string', ['limit' => 255, 'null' => false])
                ->addColumn('state_id', 'integer', $mediumInt + ['null' => false])
                ->addColumn('state_code', 'string', ['limit' => 255, 'null' => false])
                ->addColumn('country_id', 'integer', $mediumInt + ['null' => false])
                ->addColumn('country_code', 'char', ['limit' => 2, 'null' => false])
                ->addColumn('type', 'string', ['limit' => 191, 'null' => true])
                ->addColumn('type_local', 'string', ['limit' => 191, 'null' => true])
                ->addColumn('level', 'integer', ['null' => true])
                ->addColumn('parent_id', 'integer', $mediumInt + ['null' => true])
                ->addColumn('latitude', 'decimal', ['precision' => 10, 'scale' => 8, 'null' => false])
                ->addColumn('longitude', 'decimal', ['precision' => 11, 'scale' => 8, 'null' => false])
                ->addColumn('native', 'string', ['limit' => 255, 'null' => true])
                ->addColumn('population', 'biginteger', ['signed' => false, 'null' => true])
                ->addColumn('timezone', 'string', ['limit' => 255, 'null' => true])
                ->addColumn('translations', 'text', ['null' => true])
                ->addColumn('created_at', 'timestamp', ['default' => '2014-01-01 12:01:01', 'null' => false])
                ->addColumn('updated_at', 'timestamp', ['default' => 'CURRENT_TIMESTAMP', 'update' => 'CURRENT_TIMESTAMP', 'null' => false])
                ->addColumn('flag', 'boolean', ['default' => true, 'null' => false])
                ->addColumn('wikiDataId', 'string', ['limit' => 255, 'null' => true])
                ->addIndex(['state_id'], ['name' => 'idx_counties_state'])
                ->addIndex(['country_id'], ['name' => 'idx_counties_country'])
                ->addIndex(['parent_id'], ['name' => 'idx_counties_parent'])
                ->addForeignKey('state_id', 'states', 'id', ['constraint' => 'counties_state_fk'])
                ->addForeignKey('country_id', 'countries', 'id', ['constraint' => 'counties_country_fk'])
                ->addForeignKey('parent_id', 'counties', 'id', ['constraint' => 'counties_parent_fk', 'delete' => 'SET_NULL'])
                ->create();
        }

        if (!$this->table('cities')->hasColumn('county_id')) {
            $this->table('cities')
                ->addColumn('county_id', 'integer', [
                    'signed' => false, 'limit' => MysqlAdapter::INT_MEDIUM, 'null' => true,
                ])
                ->addIndex(['county_id'], ['name' => 'idx_cities_county'])
                ->addForeignKey('county_id', 'counties', 'id', [
                    'constraint' => 'cities_county_fk', 'delete' => 'SET_NULL',
                ])
                ->update();
        }
    }

    /** Remove dependent city links before dropping counties; contribution JSON remains the backup. */
    public function down(): void
    {
        if ($this->table('cities')->hasColumn('county_id')) {
            $this->table('cities')->dropForeignKey('county_id')->removeColumn('county_id')->update();
        }
        if ($this->hasTable('counties')) {
            $this->table('counties')->drop()->save();
        }
    }
}
