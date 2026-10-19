-- Table: county_states


            IF OBJECT_ID('world.county_states', 'U') IS NOT NULL DROP TABLE world.county_states;
            CREATE TABLE world.county_states (
                county_id INT NOT NULL,
                state_id INT NOT NULL,
                CONSTRAINT PK_county_states PRIMARY KEY (county_id, state_id),
                CONSTRAINT FK_county_states_counties FOREIGN KEY (county_id) REFERENCES world.counties(id) ON DELETE CASCADE,
                CONSTRAINT FK_county_states_states FOREIGN KEY (state_id) REFERENCES world.states(id)
            );

INSERT INTO world.county_states (county_id, state_id) VALUES
(14023, 4060),
(14023, 4061),
(14024, 4060),
(14024, 4061),
(14024, 4074),
(14024, 4075),
(14025, 4061),
(14025, 4074),
(14026, 4060),
(14026, 4069),
(14027, 4060),
(14027, 4075),
(14028, 4060),
(14028, 4065),
(14029, 4062),
(14029, 4066);

