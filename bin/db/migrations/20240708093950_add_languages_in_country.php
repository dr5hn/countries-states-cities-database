<?php

declare(strict_types=1);

use Phinx\Migration\AbstractMigration;

final class AddLanguagesInCountry extends AbstractMigration
{
    /**
     * Change Method.
     *
     * Write your reversible migrations using this method.
     *
     * More information on writing migrations is available here:
     * https://book.cakephp.org/phinx/0/en/migrations.html#the-change-method
     *
     * Remember to call "create()" or "update()" and NOT "save()" when working
     * with the Table class.
     */
    public function change(): void
    {
        $table = $this->table('countries');
        if (!$table->hasColumn('language')) {
            $table->addColumn(
                'language',
                'string',
                ['limit' => 5, 'default' => null, 'null' => true, 'after' => 'currency_symbol']
            )
                ->update();
        }

        $sql1="
                UPDATE countries SET language = 'hy-AM' WHERE iso3 ='ARM'; 
                UPDATE countries SET language = 'ru-RU' WHERE iso3 ='RUS'; 
                UPDATE countries SET language = 'en-US' WHERE iso3 ='USA'; 
                UPDATE countries SET language = 'en-GB' WHERE iso3 ='GBR'; 
                UPDATE countries SET language = 'it-IT' WHERE iso3 ='ITA'; 
                UPDATE countries SET language = 'fr-FR' WHERE iso3 ='FRA'; 
                ";

        $this->execute($sql1);
    }
}
