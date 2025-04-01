-- MySQL dump 10.13  Distrib 8.0.41, for Linux (x86_64)
--
-- Host: localhost    Database: world
-- ------------------------------------------------------
-- Server version	8.0.41-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `regions` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
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
INSERT INTO `regions` VALUES (1,'Africa','{\"ko\":\"아프리카\",\"pt-BR\":\"África\",\"pt\":\"África\",\"nl\":\"Afrika\",\"hr\":\"Afrika\",\"fa\":\"آفریقا\",\"de\":\"Afrika\",\"es\":\"África\",\"fr\":\"Afrique\",\"ja\":\"アフリカ\",\"it\":\"Africa\",\"zh-CN\":\"非洲\",\"tr\":\"Afrika\",\"ru\":\"Африка\",\"uk\":\"Африка\",\"pl\":\"Afryka\"}','2023-08-14 10:41:03','2023-08-14 10:41:03',1,'Q15'),(2,'Americas','{\"ko\":\"아메리카\",\"pt-BR\":\"América\",\"pt\":\"América\",\"nl\":\"Amerika\",\"hr\":\"Amerika\",\"fa\":\"قاره آمریکا\",\"de\":\"Amerika\",\"es\":\"América\",\"fr\":\"Amérique\",\"ja\":\"アメリカ州\",\"it\":\"America\",\"zh-CN\":\"美洲\",\"tr\":\"Amerika\",\"ru\":\"Америка\",\"uk\":\"Америка\",\"pl\":\"Ameryka\"}','2023-08-14 10:41:03','2024-06-16 04:09:55',1,'Q828'),(3,'Asia','{\"ko\":\"아시아\",\"pt-BR\":\"Ásia\",\"pt\":\"Ásia\",\"nl\":\"Azië\",\"hr\":\"Ázsia\",\"fa\":\"آسیا\",\"de\":\"Asien\",\"es\":\"Asia\",\"fr\":\"Asie\",\"ja\":\"アジア\",\"it\":\"Asia\",\"zh-CN\":\"亚洲\",\"tr\":\"Asya\",\"ru\":\"Азия\",\"uk\":\"Азія\",\"pl\":\"Azja\"}','2023-08-14 10:41:03','2023-08-14 10:41:03',1,'Q48'),(4,'Europe','{\"ko\":\"유럽\",\"pt-BR\":\"Europa\",\"pt\":\"Europa\",\"nl\":\"Europa\",\"hr\":\"Európa\",\"fa\":\"اروپا\",\"de\":\"Europa\",\"es\":\"Europa\",\"fr\":\"Europe\",\"ja\":\"ヨーロッパ\",\"it\":\"Europa\",\"zh-CN\":\"欧洲\",\"tr\":\"Avrupa\",\"ru\":\"Европа\",\"uk\":\"Європа\",\"pl\":\"Europa\"}','2023-08-14 10:41:03','2023-08-14 10:41:03',1,'Q46'),(5,'Oceania','{\"ko\":\"오세아니아\",\"pt-BR\":\"Oceania\",\"pt\":\"Oceania\",\"nl\":\"Oceanië en Australië\",\"hr\":\"Óceánia és Ausztrália\",\"fa\":\"اقیانوسیه\",\"de\":\"Ozeanien und Australien\",\"es\":\"Oceanía\",\"fr\":\"Océanie\",\"ja\":\"オセアニア\",\"it\":\"Oceania\",\"zh-CN\":\"大洋洲\",\"tr\":\"Okyanusya\",\"ru\":\"Океания\",\"uk\":\"Океанія\",\"pl\":\"Oceania\"}','2023-08-14 10:41:03','2023-08-14 10:41:03',1,'Q55643'),(6,'Polar','{\"ko\":\"남극\",\"pt-BR\":\"Antártida\",\"pt\":\"Antártida\",\"nl\":\"Antarctica\",\"hr\":\"Antarktika\",\"fa\":\"جنوبگان\",\"de\":\"Antarktika\",\"es\":\"Antártida\",\"fr\":\"Antarctique\",\"ja\":\"南極大陸\",\"it\":\"Antartide\",\"zh-CN\":\"南極洲\",\"tr\":\"Antarktika\",\"ru\":\"Антарктика\",\"uk\":\"Антарктика\",\"pl\":\"Antarktyka\"}','2023-08-14 10:41:03','2024-06-16 04:20:26',1,'Q51');
/*!40000 ALTER TABLE `regions` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-01  8:59:15
