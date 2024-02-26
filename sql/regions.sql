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
-- Table structure for table `regions`
--

DROP TABLE IF EXISTS `regions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `regions` (
  `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `translations` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `flag` tinyint(1) NOT NULL DEFAULT '1',
  `wikiDataId` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Rapid API GeoDB Cities',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `regions`
--

/*!40000 ALTER TABLE `regions` DISABLE KEYS */;
INSERT INTO `regions` VALUES (1,'Africa','{\"kr\":\"아프리카\",\"pt-BR\":\"África\",\"pt\":\"África\",\"nl\":\"Afrika\",\"hr\":\"Afrika\",\"fa\":\"آفریقا\",\"de\":\"Afrika\",\"es\":\"África\",\"fr\":\"Afrique\",\"ja\":\"アフリカ\",\"it\":\"Africa\",\"cn\":\"非洲\",\"tr\":\"Afrika\"}','2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q15'),(2,'Americas','{\"kr\":\"아메리카\",\"pt-BR\":\"América\",\"pt\":\"América\",\"nl\":\"Amerika\",\"hr\":\"Amerika\",\"fa\":\"قاره آمریکا\",\"de\":\"Amerika\",\"es\":\"América\",\"fr\":\"Amérique\",\"ja\":\"アメリカ州\",\"it\":\"America\",\"cn\":\"美洲\",\"tr\":\"Amerika\"}','2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q828'),(3,'Asia','{\"kr\":\"아시아\",\"pt-BR\":\"Ásia\",\"pt\":\"Ásia\",\"nl\":\"Azië\",\"hr\":\"Ázsia\",\"fa\":\"آسیا\",\"de\":\"Asien\",\"es\":\"Asia\",\"fr\":\"Asie\",\"ja\":\"アジア\",\"it\":\"Asia\",\"cn\":\"亚洲\",\"tr\":\"Asya\"}','2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q48'),(4,'Europe','{\"kr\":\"유럽\",\"pt-BR\":\"Europa\",\"pt\":\"Europa\",\"nl\":\"Europa\",\"hr\":\"Európa\",\"fa\":\"اروپا\",\"de\":\"Europa\",\"es\":\"Europa\",\"fr\":\"Europe\",\"ja\":\"ヨーロッパ\",\"it\":\"Europa\",\"cn\":\"欧洲\",\"tr\":\"Avrupa\"}','2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q46'),(5,'Oceania','{\"kr\":\"오세아니아\",\"pt-BR\":\"Oceania\",\"pt\":\"Oceania\",\"nl\":\"Oceanië en Australië\",\"hr\":\"Óceánia és Ausztrália\",\"fa\":\"اقیانوسیه\",\"de\":\"Ozeanien und Australien\",\"es\":\"Oceanía\",\"fr\":\"Océanie\",\"ja\":\"オセアニア\",\"it\":\"Oceania\",\"cn\":\"大洋洲\",\"tr\":\"Okyanusya\"}','2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q55643'),(6,'Polar','{\"kr\":\"남극\",\"pt-BR\":\"Antártida\",\"pt\":\"Antártida\",\"nl\":\"Antarctica\",\"hr\":\"Antarktika\",\"fa\":\"جنوبگان\",\"de\":\"Antarktika\",\"es\":\"Antártida\",\"fr\":\"Antarctique\",\"ja\":\"南極大陸\",\"it\":\"Antartide\",\"cn\":\"南極洲\",\"tr\":\"Antarktika\"}','2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q51');
/*!40000 ALTER TABLE `regions` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-02-26 13:28:12
