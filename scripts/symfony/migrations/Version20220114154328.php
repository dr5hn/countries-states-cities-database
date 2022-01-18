<?php

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20220114154328 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Create the countries table.';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TABLE countries (
            id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, 
            name VARCHAR(100) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            iso3 VARCHAR(3) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            numeric_code VARCHAR(3) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            iso2 VARCHAR(2) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            phonecode VARCHAR(255) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            capital VARCHAR(255) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            currency VARCHAR(255) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            currency_name VARCHAR(255) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            currency_symbol VARCHAR(255) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            tld VARCHAR(255) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            native VARCHAR(255) DEFAULT NULL COLLATE `utf8mb4_unicode_ci`, 
            region VARCHAR(255) DEFAULT NULL COLLATE `utf8mb4_unicode_ci`, 
            subregion VARCHAR(255) DEFAULT NULL COLLATE `utf8mb4_unicode_ci`, 
            timezones LONGTEXT NOT NULL, 
            translations LONGTEXT NOT NULL, 
            latitude NUMERIC(10, 8) NOT NULL, 
            longitude NUMERIC(11, 8) NOT NULL, 
            emoji VARCHAR(191) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            emojiU VARCHAR(191) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
            created_at DATETIME NOT NULL, 
            updated_at DATETIME NOT NULL, 
            flag TINYINT(1) DEFAULT \'1\' NOT NULL, 
            wikiDataId VARCHAR(255) DEFAULT NULL COLLATE `utf8mb4_unicode_ci`, 
            PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('DROP TABLE countries');
    }
}
