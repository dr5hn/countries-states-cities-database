<?php

declare(strict_types=1);

use Phinx\Migration\AbstractMigration;
use Phinx\Db\Adapter\MysqlAdapter;

/** v5.0.0: a city of a country with no states (e.g. Western Sahara) stores state_id and state_code as NULL. */
final class NullableCityState extends AbstractMigration
{
    /** Allow NULL in cities.state_id and cities.state_code; the foreign key to states stays. */
    public function up(): void
    {
        $mediumInt = ['signed' => false, 'limit' => MysqlAdapter::INT_MEDIUM];
        $this->table('cities')
            ->changeColumn('state_id', 'integer', $mediumInt + ['null' => true, 'default' => null])
            ->changeColumn('state_code', 'string', ['limit' => 255, 'null' => true, 'default' => null])
            ->update();
        // the pair is set together or null together
        $this->execute('ALTER TABLE cities ADD CONSTRAINT cities_state_pair CHECK ' .
            '((state_id IS NULL AND state_code IS NULL) OR (state_id IS NOT NULL AND state_code IS NOT NULL))');
    }

    /** Restore NOT NULL; refuses while any city has no state, so no row is lost or invented. */
    public function down(): void
    {
        $rows = $this->fetchRow('SELECT COUNT(*) AS n FROM cities WHERE state_id IS NULL OR state_code IS NULL');
        if ((int) $rows['n'] > 0) {
            throw new \RuntimeException("{$rows['n']} cities have no state; move them to a state before reverting this migration");
        }
        $this->execute('ALTER TABLE cities DROP CHECK cities_state_pair');
        $mediumInt = ['signed' => false, 'limit' => MysqlAdapter::INT_MEDIUM];
        $this->table('cities')
            ->changeColumn('state_id', 'integer', $mediumInt + ['null' => false])
            ->changeColumn('state_code', 'string', ['limit' => 255, 'null' => false])
            ->update();
    }
}
