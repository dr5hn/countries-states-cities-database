<?php

declare(strict_types=1);

use Phinx\Migration\AbstractMigration;

/**
 * Creates the `postcodes` table for issue #1039.
 *
 * Stores postal codes as their own entity (Tier 4 architecture):
 * one row per postcode, foreign-keyed to country (required) and
 * state/city (both nullable to handle country-only and disputed regions).
 *
 * Mirrors the column conventions of the `cities` table (denormalised
 * country_code/state_code, lat/lng decimals, auto-managed timestamps).
 */
final class CreatePostcodesTable extends AbstractMigration
{
    public function change(): void
    {
        if ($this->hasTable('postcodes')) {
            return;
        }

        $this->table('postcodes', [
                'id'          => false,
                'primary_key' => ['id'],
                'engine'      => 'InnoDB',
                'collation'   => 'utf8mb4_unicode_ci',
                'comment'     => 'Postal codes (issue #1039) — Tier 4: one row per postcode',
            ])
            ->addColumn('id', 'integer', [
                'identity' => true,
                'signed'   => false,
                'limit'    => \Phinx\Db\Adapter\MysqlAdapter::INT_REGULAR,
            ])
            ->addColumn('code', 'string', [
                'limit'   => 20,
                'null'    => false,
                'comment' => 'The postal code value (alphanumeric, country-specific format)',
            ])
            ->addColumn('country_id', 'integer', [
                'signed' => false,
                'limit'  => \Phinx\Db\Adapter\MysqlAdapter::INT_MEDIUM,
                'null'   => false,
            ])
            ->addColumn('country_code', 'char', [
                'limit' => 2,
                'null'  => false,
            ])
            ->addColumn('state_id', 'integer', [
                'signed'  => false,
                'limit'   => \Phinx\Db\Adapter\MysqlAdapter::INT_MEDIUM,
                'null'    => true,
                'default' => null,
            ])
            ->addColumn('state_code', 'string', [
                'limit'   => 255,
                'null'    => true,
                'default' => null,
            ])
            ->addColumn('city_id', 'integer', [
                'signed'  => false,
                'limit'   => \Phinx\Db\Adapter\MysqlAdapter::INT_MEDIUM,
                'null'    => true,
                'default' => null,
            ])
            ->addColumn('locality_name', 'string', [
                'limit'   => 255,
                'null'    => true,
                'default' => null,
                'comment' => 'Human-readable place name associated with the postcode',
            ])
            ->addColumn('type', 'string', [
                'limit'   => 32,
                'null'    => true,
                'default' => null,
                'comment' => 'Granularity: full | outward | sector | district | area',
            ])
            ->addColumn('latitude', 'decimal', [
                'precision' => 10,
                'scale'     => 8,
                'null'      => true,
                'default'   => null,
            ])
            ->addColumn('longitude', 'decimal', [
                'precision' => 11,
                'scale'     => 8,
                'null'      => true,
                'default'   => null,
            ])
            ->addColumn('source', 'string', [
                'limit'   => 64,
                'null'    => true,
                'default' => null,
                'comment' => 'Originating data source for license/attribution tracking (e.g. openplz, wikidata, census)',
            ])
            ->addColumn('wikiDataId', 'string', [
                'limit'   => 255,
                'null'    => true,
                'default' => null,
                'comment' => 'Wikidata Q-ID for cross-referencing',
            ])
            ->addColumn('created_at', 'timestamp', [
                'default' => '2014-01-01 12:01:01',
                'null'    => false,
            ])
            ->addColumn('updated_at', 'timestamp', [
                'default' => 'CURRENT_TIMESTAMP',
                'update'  => 'CURRENT_TIMESTAMP',
                'null'    => false,
            ])
            ->addColumn('flag', 'boolean', [
                'default' => true,
                'null'    => false,
            ])
            ->addIndex(['code'], ['name' => 'idx_postcodes_code'])
            ->addIndex(['country_id', 'code'], ['name' => 'idx_postcodes_country_code'])
            ->addIndex(['state_id'], ['name' => 'idx_postcodes_state'])
            ->addIndex(['city_id'], ['name' => 'idx_postcodes_city'])
            ->addForeignKey('country_id', 'countries', 'id', [
                'constraint' => 'postcodes_country_fk',
            ])
            ->addForeignKey('state_id', 'states', 'id', [
                'constraint' => 'postcodes_state_fk',
                'delete'     => 'SET_NULL',
                'update'     => 'NO_ACTION',
            ])
            ->addForeignKey('city_id', 'cities', 'id', [
                'constraint' => 'postcodes_city_fk',
                'delete'     => 'SET_NULL',
                'update'     => 'NO_ACTION',
            ])
            ->create();
    }
}
