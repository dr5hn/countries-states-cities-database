<?php

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20220115121847 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('
                CREATE TABLE cities (
                id BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, 
                state_id BIGINT UNSIGNED DEFAULT NULL, 
                country_id BIGINT UNSIGNED DEFAULT NULL, 
                name VARCHAR(255) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
                state_code VARCHAR(10) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
                country_code VARCHAR(2) NOT NULL COLLATE `utf8mb4_unicode_ci`, 
                latitude NUMERIC(10, 8) DEFAULT NULL, 
                longitude NUMERIC(11, 8) DEFAULT NULL, 
                created_at DATETIME NOT NULL, 
                updated_at DATETIME NOT NULL, 
                flag TINYINT(1) DEFAULT \'1\' NOT NULL, 
                wikiDataId VARCHAR(255) DEFAULT NULL COLLATE `utf8mb4_unicode_ci`, 
                INDEX IDX_D95DB16B5D83CC1 (state_id), INDEX IDX_D95DB16BF92F3E70 (country_id), 
                PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8mb4 COLLATE `utf8mb4_unicode_ci` ENGINE = InnoDB');

        $this->addSql('ALTER TABLE cities ADD CONSTRAINT FK_D95DB16B5D83CC1 FOREIGN KEY (state_id) REFERENCES states (id)');
        $this->addSql('ALTER TABLE cities ADD CONSTRAINT FK_D95DB16BF92F3E70 FOREIGN KEY (country_id) REFERENCES countries (id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('DROP TABLE cities');
    }
}
