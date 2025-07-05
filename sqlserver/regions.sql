-- Table: regions


            IF OBJECT_ID('world.regions', 'U') IS NOT NULL DROP TABLE world.regions;
            CREATE TABLE world.regions (
                id INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(100) NOT NULL,
                translations NVARCHAR(MAX),
                created_at DATETIME2 NULL,
                updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
                flag BIT NOT NULL DEFAULT 1,
                wikiDataId NVARCHAR(255) NULL
            );

SET IDENTITY_INSERT world.regions ON;

INSERT INTO world.regions (id, name, translations, wikiDataId) VALUES
(1, N'Africa', N'{"br":"Afrika","ko":"\uc544\ud504\ub9ac\uce74","pt-BR":"\u00c1frica","pt":"\u00c1frica","nl":"Afrika","hr":"Afrika","fa":"\u0622\u0641\u0631\u06cc\u0642\u0627","de":"Afrika","es":"\u00c1frica","fr":"Afrique","ja":"\u30a2\u30d5\u30ea\u30ab","it":"Africa","zh-CN":"\u975e\u6d32","tr":"Afrika","ru":"\u0410\u0444\u0440\u0438\u043a\u0430","uk":"\u0410\u0444\u0440\u0438\u043a\u0430","pl":"Afryka"}', N'Q15'),
(2, N'Americas', N'{"br":"Amerika","ko":"\uc544\uba54\ub9ac\uce74","pt-BR":"Am\u00e9rica","pt":"Am\u00e9rica","nl":"Amerika","hr":"Amerika","fa":"\u0642\u0627\u0631\u0647 \u0622\u0645\u0631\u06cc\u06a9\u0627","de":"Amerika","es":"Am\u00e9rica","fr":"Am\u00e9rique","ja":"\u30a2\u30e1\u30ea\u30ab\u5dde","it":"America","zh-CN":"\u7f8e\u6d32","tr":"Amerika","ru":"\u0410\u043c\u0435\u0440\u0438\u043a\u0430","uk":"\u0410\u043c\u0435\u0440\u0438\u043a\u0430","pl":"Ameryka"}', N'Q828'),
(3, N'Asia', N'{"br":"Azia","ko":"\uc544\uc2dc\uc544","pt-BR":"\u00c1sia","pt":"\u00c1sia","nl":"Azi\u00eb","hr":"\u00c1zsia","fa":"\u0622\u0633\u06cc\u0627","de":"Asien","es":"Asia","fr":"Asie","ja":"\u30a2\u30b8\u30a2","it":"Asia","zh-CN":"\u4e9a\u6d32","tr":"Asya","ru":"\u0410\u0437\u0438\u044f","uk":"\u0410\u0437\u0456\u044f","pl":"Azja"}', N'Q48'),
(4, N'Europe', N'{"br":"Europa","ko":"\uc720\ub7fd","pt-BR":"Europa","pt":"Europa","nl":"Europa","hr":"Eur\u00f3pa","fa":"\u0627\u0631\u0648\u067e\u0627","de":"Europa","es":"Europa","fr":"Europe","ja":"\u30e8\u30fc\u30ed\u30c3\u30d1","it":"Europa","zh-CN":"\u6b27\u6d32","tr":"Avrupa","ru":"\u0415\u0432\u0440\u043e\u043f\u0430","uk":"\u0404\u0432\u0440\u043e\u043f\u0430","pl":"Europa"}', N'Q46'),
(5, N'Oceania', N'{"br":"Okeania","ko":"\uc624\uc138\uc544\ub2c8\uc544","pt-BR":"Oceania","pt":"Oceania","nl":"Oceani\u00eb en Australi\u00eb","hr":"\u00d3ce\u00e1nia \u00e9s Ausztr\u00e1lia","fa":"\u0627\u0642\u06cc\u0627\u0646\u0648\u0633\u06cc\u0647","de":"Ozeanien und Australien","es":"Ocean\u00eda","fr":"Oc\u00e9anie","ja":"\u30aa\u30bb\u30a2\u30cb\u30a2","it":"Oceania","zh-CN":"\u5927\u6d0b\u6d32","tr":"Okyanusya","ru":"\u041e\u043a\u0435\u0430\u043d\u0438\u044f","uk":"\u041e\u043a\u0435\u0430\u043d\u0456\u044f","pl":"Oceania"}', N'Q55643'),
(6, N'Polar', N'{"br":"Antartika","ko":"\ub0a8\uadf9","pt-BR":"Ant\u00e1rtida","pt":"Ant\u00e1rtida","nl":"Antarctica","hr":"Antarktika","fa":"\u062c\u0646\u0648\u0628\u06af\u0627\u0646","de":"Antarktika","es":"Ant\u00e1rtida","fr":"Antarctique","ja":"\u5357\u6975\u5927\u9678","it":"Antartide","zh-CN":"\u5357\u6975\u6d32","tr":"Antarktika","ru":"\u0410\u043d\u0442\u0430\u0440\u043a\u0442\u0438\u043a\u0430","uk":"\u0410\u043d\u0442\u0430\u0440\u043a\u0442\u0438\u043a\u0430","pl":"Antarktyka"}', N'Q51');

SET IDENTITY_INSERT world.regions OFF;

