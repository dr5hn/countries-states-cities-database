<?php

declare(strict_types=1);

use Phinx\Migration\AbstractMigration;

/**
 * Adds `translations_capital` and `translations_currency_name` to `countries`
 * for issue #1627 — localized names for capital cities and currency names,
 * following the existing `translations` (country name) column's shape and type.
 */
final class AddCapitalCurrencyTranslationsToCountries extends AbstractMigration
{
    public function change(): void
    {
        $table = $this->table('countries');

        if (!$table->hasColumn('translations_capital')) {
            $table->addColumn(
                'translations_capital',
                'text',
                ['null' => true, 'default' => null, 'after' => 'translations']
            )->update();
        }

        if (!$table->hasColumn('translations_currency_name')) {
            $table->addColumn(
                'translations_currency_name',
                'text',
                ['null' => true, 'default' => null, 'after' => 'translations_capital']
            )->update();
        }
    }
}
