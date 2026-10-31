<?php

declare(strict_types=1);

use Phinx\Migration\AbstractMigration;
use Phinx\Db\Adapter\MysqlAdapter;

/**
 * v5.0.0 (decision B6): a county of several regions, such as New Zealand's district councils that cross regional
 * boundaries, stores state_id and state_code as NULL and lists its regions in county_states, one row per
 * (county_id, state_id). A county with its own state has no rows there.
 */
final class CountyStates extends AbstractMigration
{
    /** Allow a null county state pair (both or neither) and create county_states with both foreign keys. */
    public function up(): void
    {
        $mediumInt = ['signed' => false, 'limit' => MysqlAdapter::INT_MEDIUM];
        $this->table('counties')
            ->changeColumn('state_id', 'integer', $mediumInt + ['null' => true, 'default' => null])
            ->changeColumn('state_code', 'string', ['limit' => 255, 'null' => true, 'default' => null])
            ->update();
        $this->execute('ALTER TABLE counties ADD CONSTRAINT counties_state_pair CHECK ' .
            '((state_id IS NULL AND state_code IS NULL) OR (state_id IS NOT NULL AND state_code IS NOT NULL))');
        $this->table('county_states', [
            'id' => false, 'primary_key' => ['county_id', 'state_id'],
            'engine' => 'InnoDB', 'collation' => 'utf8mb4_unicode_ci',
        ])
            ->addColumn('county_id', 'integer', $mediumInt + ['null' => false])
            ->addColumn('state_id', 'integer', $mediumInt + ['null' => false])
            ->addIndex(['state_id'], ['name' => 'idx_county_states_state'])
            ->addForeignKey('county_id', 'counties', 'id', ['delete' => 'CASCADE', 'constraint' => 'county_states_county_fk'])
            ->addForeignKey('state_id', 'states', 'id', ['constraint' => 'county_states_state_fk'])
            ->create();
    }

    /** Restore one state per county; refuses while any county has no state or any region row exists. */
    public function down(): void
    {
        $open = $this->fetchRow('SELECT (SELECT COUNT(*) FROM counties WHERE state_id IS NULL OR state_code IS NULL) AS counties, ' .
            '(SELECT COUNT(*) FROM county_states) AS links');
        if ((int) $open['counties'] > 0 || (int) $open['links'] > 0) {
            throw new \RuntimeException("{$open['counties']} counties have no state and {$open['links']} region rows exist; " .
                'give each county one state before reverting this migration');
        }
        $this->table('county_states')->drop()->save();
        $this->execute('ALTER TABLE counties DROP CHECK counties_state_pair');
        $mediumInt = ['signed' => false, 'limit' => MysqlAdapter::INT_MEDIUM];
        $this->table('counties')
            ->changeColumn('state_id', 'integer', $mediumInt + ['null' => false])
            ->changeColumn('state_code', 'string', ['limit' => 255, 'null' => false])
            ->update();
    }
}
