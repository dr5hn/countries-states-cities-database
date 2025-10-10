<?php

declare(strict_types=1);

use Phinx\Migration\AbstractMigration;

final class FixInvalidTimezones extends AbstractMigration
{
    /**
     * Fix invalid and inconsistent timezones in states table.
     * Replace Etc/GMT timezones with proper IANA canonical timezones.
     * Replace America/Kralendijk (non-standard) with America/Curacao.
     */
    public function change(): void
    {
        $sql = "
            -- Costa Rica (CR) - Puntarenas: Etc/GMT+6 → America/Costa_Rica
            UPDATE states SET timezone = 'America/Costa_Rica' WHERE id = 1210;
            
            -- Kiribati (KI) - Gilbert: Etc/GMT-12 → Pacific/Tarawa
            UPDATE states SET timezone = 'Pacific/Tarawa' WHERE id = 1831;
            
            -- Morocco (MA) - Dakhla-Oued Ed-Dahab (EH): Etc/GMT+1 → Africa/El_Aaiun
            UPDATE states SET timezone = 'Africa/El_Aaiun' WHERE id = 3306;
            
            -- India (IN) - Lakshadweep: Etc/GMT-5 → Asia/Kolkata
            UPDATE states SET timezone = 'Asia/Kolkata' WHERE id = 4019;
            
            -- Palau (PW) - All states: Etc/GMT-9 → Pacific/Palau
            UPDATE states SET timezone = 'Pacific/Palau' WHERE id IN (4527, 4530, 4531, 4533, 4534, 4536, 4537, 4540, 4541);
            
            -- France (FR) - Clipperton: Etc/GMT+7 → America/Tijuana
            UPDATE states SET timezone = 'America/Tijuana' WHERE id = 5064;
            
            -- Bonaire, Sint Eustatius and Saba (BQ): America/Kralendijk → America/Curacao
            UPDATE states SET timezone = 'America/Curacao' WHERE id IN (5086, 5087, 5088);
            
            -- United States Minor Outlying Islands (UM) - Baker, Howland: Etc/GMT+12 → Etc/UTC
            -- These islands are at UTC-12, but there's no proper IANA timezone for them
            UPDATE states SET timezone = 'Etc/UTC' WHERE id IN (5212, 5213);
            
            -- United States Minor Outlying Islands (UM) - Jarvis, Kingman, Palmyra: Etc/GMT+11 → Pacific/Midway
            UPDATE states SET timezone = 'Pacific/Midway' WHERE id IN (5214, 5216, 5219);
            
            -- American Samoa (AS) - Rose: Etc/GMT+11 → Pacific/Pago_Pago
            UPDATE states SET timezone = 'Pacific/Pago_Pago' WHERE id = 5378;
            
            -- Greenland (GL) - Qeqertalik: Etc/GMT+4 → America/Nuuk
            UPDATE states SET timezone = 'America/Nuuk' WHERE id = 5381;
        ";

        $this->execute($sql);
    }
}
