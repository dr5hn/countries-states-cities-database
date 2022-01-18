<?php

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20220115112200 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('
                CREATE TABLE states (
                id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, 
                country_id BIGINT UNSIGNED DEFAULT NULL, 
                name VARCHAR(255) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
                country_code VARCHAR(2) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
                fips_code VARCHAR(255) DEFAULT NULL COLLATE `utf8mb4_unicode_ci`, 
                iso2 VARCHAR(10) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
                type VARCHAR(191) DEFAULT NULL COLLATE `utf8mb4_unicode_ci`, 
                latitude NUMERIC(10, 8) DEFAULT NULL, 
                longitude NUMERIC(11, 8) DEFAULT NULL, 
                created_at DATETIME NOT NULL, 
                updated_at DATETIME NOT NULL, 
                flag TINYINT(1) DEFAULT \'1\' NOT NULL, 
                wikiDataId VARCHAR(255) DEFAULT NULL COLLATE `utf8mb4_unicode_ci`, 
                INDEX IDX_31C2774DF92F3E70 (country_id), 
                PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');
        $this->addSql('ALTER TABLE states ADD CONSTRAINT FK_31C2774DF92F3E70 FOREIGN KEY (country_id) REFERENCES countries (id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('DROP TABLE states');
    }
}
