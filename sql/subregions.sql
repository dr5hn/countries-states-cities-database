-- MySQL dump 10.13  Distrib 5.7.44, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: world
-- ------------------------------------------------------
-- Server version	5.7.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `subregions`
--

DROP TABLE IF EXISTS `subregions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subregions` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `translations` text COLLATE utf8mb4_unicode_ci,
  `region_id` mediumint(8) unsigned NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `flag` tinyint(1) NOT NULL DEFAULT '1',
  `wikiDataId` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Rapid API GeoDB Cities',
  PRIMARY KEY (`id`),
  KEY `subregion_continent` (`region_id`),
  CONSTRAINT `subregion_continent_final` FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subregions`
--

/*!40000 ALTER TABLE `subregions` DISABLE KEYS */;
INSERT INTO `subregions` VALUES (1,'Northern Africa','{\"korean\":\"북아프리카\",\"portuguese\":\"Norte de África\",\"dutch\":\"Noord-Afrika\",\"croatian\":\"Sjeverna Afrika\",\"persian\":\"شمال آفریقا\",\"german\":\"Nordafrika\",\"spanish\":\"Norte de África\",\"french\":\"Afrique du Nord\",\"japanese\":\"北アフリカ\",\"italian\":\"Nordafrica\",\"chinese\":\"北部非洲\"}',1,'2023-08-14 07:11:03','2023-08-24 20:10:23',1,'Q27381'),(2,'Middle Africa','{\"korean\":\"중앙아프리카\",\"portuguese\":\"África Central\",\"dutch\":\"Centraal-Afrika\",\"croatian\":\"Srednja Afrika\",\"persian\":\"مرکز آفریقا\",\"german\":\"Zentralafrika\",\"spanish\":\"África Central\",\"french\":\"Afrique centrale\",\"japanese\":\"中部アフリカ\",\"italian\":\"Africa centrale\",\"chinese\":\"中部非洲\"}',1,'2023-08-14 07:11:03','2023-08-24 20:22:09',1,'Q27433'),(3,'Western Africa','{\"korean\":\"서아프리카\",\"portuguese\":\"África Ocidental\",\"dutch\":\"West-Afrika\",\"croatian\":\"Zapadna Afrika\",\"persian\":\"غرب آفریقا\",\"german\":\"Westafrika\",\"spanish\":\"África Occidental\",\"french\":\"Afrique de l\'Ouest\",\"japanese\":\"西アフリカ\",\"italian\":\"Africa occidentale\",\"chinese\":\"西非\"}',1,'2023-08-14 07:11:03','2023-08-24 20:22:09',1,'Q4412'),(4,'Eastern Africa','{\"korean\":\"동아프리카\",\"portuguese\":\"África Oriental\",\"dutch\":\"Oost-Afrika\",\"croatian\":\"Istočna Afrika\",\"persian\":\"شرق آفریقا\",\"german\":\"Ostafrika\",\"spanish\":\"África Oriental\",\"french\":\"Afrique de l\'Est\",\"japanese\":\"東アフリカ\",\"italian\":\"Africa orientale\",\"chinese\":\"东部非洲\"}',1,'2023-08-14 07:11:03','2023-08-24 20:22:10',1,'Q27407'),(5,'Southern Africa','{\"korean\":\"남아프리카\",\"portuguese\":\"África Austral\",\"dutch\":\"Zuidelijk Afrika\",\"croatian\":\"Južna Afrika\",\"persian\":\"جنوب آفریقا\",\"german\":\"Südafrika\",\"spanish\":\"África austral\",\"french\":\"Afrique australe\",\"japanese\":\"南部アフリカ\",\"italian\":\"Africa australe\",\"chinese\":\"南部非洲\"}',1,'2023-08-14 07:11:03','2023-08-24 20:22:10',1,'Q27394'),(6,'Northern America','{\"korean\":\"북미\",\"portuguese\":\"América Setentrional\",\"dutch\":\"Noord-Amerika\",\"persian\":\"شمال آمریکا\",\"german\":\"Nordamerika\",\"spanish\":\"América Norteña\",\"french\":\"Amérique septentrionale\",\"japanese\":\"北部アメリカ\",\"italian\":\"America settentrionale\",\"chinese\":\"北美地區\"}',2,'2023-08-14 07:11:03','2023-08-24 20:22:10',1,'Q2017699'),(7,'Caribbean','{\"korean\":\"카리브\",\"portuguese\":\"Caraíbas\",\"dutch\":\"Caraïben\",\"croatian\":\"Karibi\",\"persian\":\"کارائیب\",\"german\":\"Karibik\",\"spanish\":\"Caribe\",\"french\":\"Caraïbes\",\"japanese\":\"カリブ海地域\",\"italian\":\"Caraibi\",\"chinese\":\"加勒比地区\"}',2,'2023-08-14 07:11:03','2023-08-24 20:22:10',1,'Q664609'),(8,'South America','{\"korean\":\"남아메리카\",\"portuguese\":\"América do Sul\",\"dutch\":\"Zuid-Amerika\",\"croatian\":\"Južna Amerika\",\"persian\":\"آمریکای جنوبی\",\"german\":\"Südamerika\",\"spanish\":\"América del Sur\",\"french\":\"Amérique du Sud\",\"japanese\":\"南アメリカ\",\"italian\":\"America meridionale\",\"chinese\":\"南美洲\"}',2,'2023-08-14 07:11:03','2023-08-24 20:22:10',1,'Q18'),(9,'Central America','{\"korean\":\"중앙아메리카\",\"portuguese\":\"América Central\",\"dutch\":\"Centraal-Amerika\",\"croatian\":\"Srednja Amerika\",\"persian\":\"آمریکای مرکزی\",\"german\":\"Zentralamerika\",\"spanish\":\"América Central\",\"french\":\"Amérique centrale\",\"japanese\":\"中央アメリカ\",\"italian\":\"America centrale\",\"chinese\":\"中美洲\"}',2,'2023-08-14 07:11:03','2023-08-24 20:22:11',1,'Q27611'),(10,'Central Asia','{\"korean\":\"중앙아시아\",\"portuguese\":\"Ásia Central\",\"dutch\":\"Centraal-Azië\",\"croatian\":\"Srednja Azija\",\"persian\":\"آسیای میانه\",\"german\":\"Zentralasien\",\"spanish\":\"Asia Central\",\"french\":\"Asie centrale\",\"japanese\":\"中央アジア\",\"italian\":\"Asia centrale\",\"chinese\":\"中亚\"}',3,'2023-08-14 07:11:03','2023-08-24 20:22:11',1,'Q27275'),(11,'Western Asia','{\"korean\":\"서아시아\",\"portuguese\":\"Sudoeste Asiático\",\"dutch\":\"Zuidwest-Azië\",\"croatian\":\"Jugozapadna Azija\",\"persian\":\"غرب آسیا\",\"german\":\"Vorderasien\",\"spanish\":\"Asia Occidental\",\"french\":\"Asie de l\'Ouest\",\"japanese\":\"西アジア\",\"italian\":\"Asia occidentale\",\"chinese\":\"西亚\"}',3,'2023-08-14 07:11:03','2023-08-24 20:22:11',1,'Q27293'),(12,'Eastern Asia','{\"korean\":\"동아시아\",\"portuguese\":\"Ásia Oriental\",\"dutch\":\"Oost-Azië\",\"croatian\":\"Istočna Azija\",\"persian\":\"شرق آسیا\",\"german\":\"Ostasien\",\"spanish\":\"Asia Oriental\",\"french\":\"Asie de l\'Est\",\"japanese\":\"東アジア\",\"italian\":\"Asia orientale\",\"chinese\":\"東亞\"}',3,'2023-08-14 07:11:03','2023-08-24 20:22:11',1,'Q27231'),(13,'South-Eastern Asia','{\"korean\":\"동남아시아\",\"portuguese\":\"Sudeste Asiático\",\"dutch\":\"Zuidoost-Azië\",\"croatian\":\"Jugoistočna Azija\",\"persian\":\"جنوب شرق آسیا\",\"german\":\"Südostasien\",\"spanish\":\"Sudeste Asiático\",\"french\":\"Asie du Sud-Est\",\"japanese\":\"東南アジア\",\"italian\":\"Sud-est asiatico\",\"chinese\":\"东南亚\"}',3,'2023-08-14 07:11:03','2023-08-24 20:22:12',1,'Q11708'),(14,'Southern Asia','{\"korean\":\"남아시아\",\"portuguese\":\"Ásia Meridional\",\"dutch\":\"Zuid-Azië\",\"croatian\":\"Južna Azija\",\"persian\":\"جنوب آسیا\",\"german\":\"Südasien\",\"spanish\":\"Asia del Sur\",\"french\":\"Asie du Sud\",\"japanese\":\"南アジア\",\"italian\":\"Asia meridionale\",\"chinese\":\"南亚\"}',3,'2023-08-14 07:11:03','2023-08-24 20:22:12',1,'Q771405'),(15,'Eastern Europe','{\"korean\":\"동유럽\",\"portuguese\":\"Europa de Leste\",\"dutch\":\"Oost-Europa\",\"croatian\":\"Istočna Europa\",\"persian\":\"شرق اروپا\",\"german\":\"Osteuropa\",\"spanish\":\"Europa Oriental\",\"french\":\"Europe de l\'Est\",\"japanese\":\"東ヨーロッパ\",\"italian\":\"Europa orientale\",\"chinese\":\"东欧\"}',4,'2023-08-14 07:11:03','2023-08-24 20:22:12',1,'Q27468'),(16,'Southern Europe','{\"korean\":\"남유럽\",\"portuguese\":\"Europa meridional\",\"dutch\":\"Zuid-Europa\",\"croatian\":\"Južna Europa\",\"persian\":\"جنوب اروپا\",\"german\":\"Südeuropa\",\"spanish\":\"Europa del Sur\",\"french\":\"Europe du Sud\",\"japanese\":\"南ヨーロッパ\",\"italian\":\"Europa meridionale\",\"chinese\":\"南欧\"}',4,'2023-08-14 07:11:03','2023-08-24 20:22:12',1,'Q27449'),(17,'Western Europe','{\"korean\":\"서유럽\",\"portuguese\":\"Europa Ocidental\",\"dutch\":\"West-Europa\",\"croatian\":\"Zapadna Europa\",\"persian\":\"غرب اروپا\",\"german\":\"Westeuropa\",\"spanish\":\"Europa Occidental\",\"french\":\"Europe de l\'Ouest\",\"japanese\":\"西ヨーロッパ\",\"italian\":\"Europa occidentale\",\"chinese\":\"西欧\"}',4,'2023-08-14 07:11:03','2023-08-24 20:22:12',1,'Q27496'),(18,'Northern Europe','{\"korean\":\"북유럽\",\"portuguese\":\"Europa Setentrional\",\"dutch\":\"Noord-Europa\",\"croatian\":\"Sjeverna Europa\",\"persian\":\"شمال اروپا\",\"german\":\"Nordeuropa\",\"spanish\":\"Europa del Norte\",\"french\":\"Europe du Nord\",\"japanese\":\"北ヨーロッパ\",\"italian\":\"Europa settentrionale\",\"chinese\":\"北歐\"}',4,'2023-08-14 07:11:03','2023-08-24 20:22:13',1,'Q27479'),(19,'Australia and New Zealand','{\"korean\":\"오스트랄라시아\",\"portuguese\":\"Australásia\",\"dutch\":\"Australazië\",\"croatian\":\"Australazija\",\"persian\":\"استرالزی\",\"german\":\"Australasien\",\"spanish\":\"Australasia\",\"french\":\"Australasie\",\"japanese\":\"オーストララシア\",\"italian\":\"Australasia\",\"chinese\":\"澳大拉西亞\"}',5,'2023-08-14 07:11:03','2023-08-24 20:22:13',1,'Q45256'),(20,'Melanesia','{\"korean\":\"멜라네시아\",\"portuguese\":\"Melanésia\",\"dutch\":\"Melanesië\",\"croatian\":\"Melanezija\",\"persian\":\"ملانزی\",\"german\":\"Melanesien\",\"spanish\":\"Melanesia\",\"french\":\"Mélanésie\",\"japanese\":\"メラネシア\",\"italian\":\"Melanesia\",\"chinese\":\"美拉尼西亚\"}',5,'2023-08-14 07:11:03','2023-08-24 20:22:13',1,'Q37394'),(21,'Micronesia','{\"korean\":\"미크로네시아\",\"portuguese\":\"Micronésia\",\"dutch\":\"Micronesië\",\"croatian\":\"Mikronezija\",\"persian\":\"میکرونزی\",\"german\":\"Mikronesien\",\"spanish\":\"Micronesia\",\"french\":\"Micronésie\",\"japanese\":\"ミクロネシア\",\"italian\":\"Micronesia\",\"chinese\":\"密克罗尼西亚群岛\"}',5,'2023-08-14 07:11:03','2023-08-24 20:22:13',1,'Q3359409'),(22,'Polynesia','{\"korean\":\"폴리네시아\",\"portuguese\":\"Polinésia\",\"dutch\":\"Polynesië\",\"croatian\":\"Polinezija\",\"persian\":\"پلی‌نزی\",\"german\":\"Polynesien\",\"spanish\":\"Polinesia\",\"french\":\"Polynésie\",\"japanese\":\"ポリネシア\",\"italian\":\"Polinesia\",\"chinese\":\"玻里尼西亞\"}',5,'2023-08-14 07:11:03','2023-08-24 20:22:13',1,'Q35942');
/*!40000 ALTER TABLE `subregions` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-02-26 13:28:12
