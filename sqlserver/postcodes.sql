-- Table: postcodes


            IF OBJECT_ID('world.postcodes', 'U') IS NOT NULL DROP TABLE world.postcodes;
            CREATE TABLE world.postcodes (
                id INT IDENTITY(1,1) PRIMARY KEY,
                code NVARCHAR(20) NOT NULL,
                country_id INT NOT NULL,
                country_code NCHAR(2) NOT NULL,
                state_id INT NULL,
                state_code NVARCHAR(255) NULL,
                city_id INT NULL,
                locality_name NVARCHAR(255) NULL,
                type NVARCHAR(32) NULL,
                latitude DECIMAL(10,8) NULL,
                longitude DECIMAL(11,8) NULL,
                source NVARCHAR(64) NULL,
                wikiDataId NVARCHAR(255) NULL,
                created_at DATETIME2 NOT NULL DEFAULT '2014-01-01 12:01:01',
                updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
                flag BIT NOT NULL DEFAULT 1,
                CONSTRAINT FK_postcodes_countries FOREIGN KEY (country_id) REFERENCES world.countries(id),
                CONSTRAINT FK_postcodes_states FOREIGN KEY (state_id) REFERENCES world.states(id),
                CONSTRAINT FK_postcodes_cities FOREIGN KEY (city_id) REFERENCES world.cities(id)
            );

SET IDENTITY_INSERT world.postcodes ON;

SET IDENTITY_INSERT world.postcodes OFF;

