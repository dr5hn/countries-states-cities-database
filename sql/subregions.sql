# ************************************************************
# Sequel Ace SQL dump
# Version 20050
#
# https://sequel-ace.com/
# https://github.com/Sequel-Ace/Sequel-Ace
#
# Host: localhost (MySQL 8.0.30)
# Database: bucketlist
# Generation Time: 2023-08-11 17:25:54 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
SET NAMES utf8mb4;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE='NO_AUTO_VALUE_ON_ZERO', SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


DROP TABLE IF EXISTS `subregions`;

CREATE TABLE `subregions` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `translations` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `region_id` mediumint unsigned NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `flag` tinyint(1) NOT NULL DEFAULT '1',
  `wikiDataId` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Rapid API GeoDB Cities',
  PRIMARY KEY (`id`),
  KEY `subregion_continent` (`region_id`),
  CONSTRAINT `subregion_continent_final` FOREIGN KEY (`region_id`) REFERENCES `regions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=251 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


/*!40000 ALTER TABLE `regions` DISABLE KEYS */;

INSERT INTO `subregions` (`id`, `name`, `translations`, `region_id`, `created_at`, `updated_at`, `flag`, `wikiDataId`)
VALUES
	(1,'Northern Africa','{\"kr\":\"북아프리카\",\"pt-BR\":\"Norte de África\",\"pt\":\"Norte de África\",\"nl\":\"Noord-Afrika\",\"hr\":\"Észak-Afrika\",\"fa\":\"شمال آفریقا\",\"de\":\"Nordafrika\",\"es\":\"Norte de África\",\"fr\":\"Afrique du Nord\",\"ja\":\"北アフリカ\",\"it\":\"Nordafrica\",\"cn\":\"北非\",\"tr\":\"Kuzey Afrika\"}',1 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q27381'),
	(2,'Middle Africa','{\"kr\":\"아프리카\",\"pt-BR\":\"África\",\"pt\":\"África\",\"nl\":\"Afrika\",\"hr\":\"Afrika\",\"fa\":\"آفریقا\",\"de\":\"Afrika\",\"es\":\"África\",\"fr\":\"Afrique\",\"ja\":\"アフリカ\",\"it\":\"Africa\",\"cn\":\"非洲\",\"tr\":\"Afrika\"}',1 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q15'),
	(3,'Western Africa','{\"kr\":\"아프리카\",\"pt-BR\":\"África\",\"pt\":\"África\",\"nl\":\"Afrika\",\"hr\":\"Afrika\",\"fa\":\"آفریقا\",\"de\":\"Afrika\",\"es\":\"África\",\"fr\":\"Afrique\",\"ja\":\"アフリカ\",\"it\":\"Africa\",\"cn\":\"非洲\",\"tr\":\"Afrika\"}',1 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q15'),
	(4,'Eastern Africa','{\"kr\":\"아프리카\",\"pt-BR\":\"África\",\"pt\":\"África\",\"nl\":\"Afrika\",\"hr\":\"Afrika\",\"fa\":\"آفریقا\",\"de\":\"Afrika\",\"es\":\"África\",\"fr\":\"Afrique\",\"ja\":\"アフリカ\",\"it\":\"Africa\",\"cn\":\"非洲\",\"tr\":\"Afrika\"}',1 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q15'),
	(5,'Southern Africa','{\"kr\":\"아프리카\",\"pt-BR\":\"África\",\"pt\":\"África\",\"nl\":\"Afrika\",\"hr\":\"Afrika\",\"fa\":\"آفریقا\",\"de\":\"Afrika\",\"es\":\"África\",\"fr\":\"Afrique\",\"ja\":\"アフリカ\",\"it\":\"Africa\",\"cn\":\"非洲\",\"tr\":\"Afrika\"}',1 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q15'),

	(6,'Northern America','{\"kr\":\"아메리카\",\"pt-BR\":\"América\",\"pt\":\"América\",\"nl\":\"Amerika\",\"hr\":\"Amerika\",\"fa\":\"قاره آمریکا\",\"de\":\"Amerika\",\"es\":\"América\",\"fr\":\"Amérique\",\"ja\":\"アメリカ州\",\"it\":\"America\",\"cn\":\"美洲\",\"tr\":\"Amerika\"}',2 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q828'),
	(7,'Caribbean','{\"kr\":\"아메리카\",\"pt-BR\":\"América\",\"pt\":\"América\",\"nl\":\"Amerika\",\"hr\":\"Amerika\",\"fa\":\"قاره آمریکا\",\"de\":\"Amerika\",\"es\":\"América\",\"fr\":\"Amérique\",\"ja\":\"アメリカ州\",\"it\":\"America\",\"cn\":\"美洲\",\"tr\":\"Amerika\"}',2 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q828'),
	(8,'South America','{\"kr\":\"아메리카\",\"pt-BR\":\"América\",\"pt\":\"América\",\"nl\":\"Amerika\",\"hr\":\"Amerika\",\"fa\":\"قاره آمریکا\",\"de\":\"Amerika\",\"es\":\"América\",\"fr\":\"Amérique\",\"ja\":\"アメリカ州\",\"it\":\"America\",\"cn\":\"美洲\",\"tr\":\"Amerika\"}',2 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q828'),
	(9,'Central America','{\"kr\":\"아메리카\",\"pt-BR\":\"América\",\"pt\":\"América\",\"nl\":\"Amerika\",\"hr\":\"Amerika\",\"fa\":\"قاره آمریکا\",\"de\":\"Amerika\",\"es\":\"América\",\"fr\":\"Amérique\",\"ja\":\"アメリカ州\",\"it\":\"America\",\"cn\":\"美洲\",\"tr\":\"Amerika\"}',2 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q828'),

	(10,'Central Asia','{\"kr\":\"아메리카\",\"pt-BR\":\"América\",\"pt\":\"América\",\"nl\":\"Amerika\",\"hr\":\"Amerika\",\"fa\":\"قاره آمریکا\",\"de\":\"Amerika\",\"es\":\"América\",\"fr\":\"Amérique\",\"ja\":\"アメリカ州\",\"it\":\"America\",\"cn\":\"美洲\",\"tr\":\"Amerika\"}',3 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q828'),
	(11,'Western Asia','{\"kr\":\"아메리카\",\"pt-BR\":\"América\",\"pt\":\"América\",\"nl\":\"Amerika\",\"hr\":\"Amerika\",\"fa\":\"قاره آمریکا\",\"de\":\"Amerika\",\"es\":\"América\",\"fr\":\"Amérique\",\"ja\":\"アメリカ州\",\"it\":\"America\",\"cn\":\"美洲\",\"tr\":\"Amerika\"}',3 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q828'),
	(12,'Eastern Asia','{\"kr\":\"아메리카\",\"pt-BR\":\"América\",\"pt\":\"América\",\"nl\":\"Amerika\",\"hr\":\"Amerika\",\"fa\":\"قاره آمریکا\",\"de\":\"Amerika\",\"es\":\"América\",\"fr\":\"Amérique\",\"ja\":\"アメリカ州\",\"it\":\"America\",\"cn\":\"美洲\",\"tr\":\"Amerika\"}',3 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q828'),
	(13,'South-Eastern Asia','{\"kr\":\"아메리카\",\"pt-BR\":\"América\",\"pt\":\"América\",\"nl\":\"Amerika\",\"hr\":\"Amerika\",\"fa\":\"قاره آمریکا\",\"de\":\"Amerika\",\"es\":\"América\",\"fr\":\"Amérique\",\"ja\":\"アメリカ州\",\"it\":\"America\",\"cn\":\"美洲\",\"tr\":\"Amerika\"}',3 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q828'),
  (14,'Southern Asia','{\"kr\":\"아메리카\",\"pt-BR\":\"América\",\"pt\":\"América\",\"nl\":\"Amerika\",\"hr\":\"Amerika\",\"fa\":\"قاره آمریکا\",\"de\":\"Amerika\",\"es\":\"América\",\"fr\":\"Amérique\",\"ja\":\"アメリカ州\",\"it\":\"America\",\"cn\":\"美洲\",\"tr\":\"Amerika\"}',3 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q828'),

	(15,'Eastern Europe','{\"kr\":\"아시아\",\"pt-BR\":\"Ásia\",\"pt\":\"Ásia\",\"nl\":\"Azië\",\"hr\":\"Ázsia\",\"fa\":\"آسیا\",\"de\":\"Asien\",\"es\":\"Asia\",\"fr\":\"Asie\",\"ja\":\"アジア\",\"it\":\"Asia\",\"cn\":\"亚洲\",\"tr\":\"Asya\"}',4 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q48'),
	(16,'Southern Europe','{\"kr\":\"아시아\",\"pt-BR\":\"Ásia\",\"pt\":\"Ásia\",\"nl\":\"Azië\",\"hr\":\"Ázsia\",\"fa\":\"آسیا\",\"de\":\"Asien\",\"es\":\"Asia\",\"fr\":\"Asie\",\"ja\":\"アジア\",\"it\":\"Asia\",\"cn\":\"亚洲\",\"tr\":\"Asya\"}',4 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q48'),
	(17,'Western Europe','{\"kr\":\"아시아\",\"pt-BR\":\"Ásia\",\"pt\":\"Ásia\",\"nl\":\"Azië\",\"hr\":\"Ázsia\",\"fa\":\"آسیا\",\"de\":\"Asien\",\"es\":\"Asia\",\"fr\":\"Asie\",\"ja\":\"アジア\",\"it\":\"Asia\",\"cn\":\"亚洲\",\"tr\":\"Asya\"}',4 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q48'),
	(18,'Northern Europe','{\"kr\":\"아시아\",\"pt-BR\":\"Ásia\",\"pt\":\"Ásia\",\"nl\":\"Azië\",\"hr\":\"Ázsia\",\"fa\":\"آسیا\",\"de\":\"Asien\",\"es\":\"Asia\",\"fr\":\"Asie\",\"ja\":\"アジア\",\"it\":\"Asia\",\"cn\":\"亚洲\",\"tr\":\"Asya\"}',4 ,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q48'),

	(19,'Australia and New Zealand','{\"kr\":\"유럽\",\"pt-BR\":\"Europa\",\"pt\":\"Europa\",\"nl\":\"Europa\",\"hr\":\"Európa\",\"fa\":\"اروپا\",\"de\":\"Europa\",\"es\":\"Europa\",\"fr\":\"Europe\",\"ja\":\"ヨーロッパ\",\"it\":\"Europa\",\"cn\":\"欧洲\",\"tr\":\"Avrupa\"}',5,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q46'),
	(20,'Melanesia','{\"kr\":\"유럽\",\"pt-BR\":\"Europa\",\"pt\":\"Europa\",\"nl\":\"Europa\",\"hr\":\"Európa\",\"fa\":\"اروپا\",\"de\":\"Europa\",\"es\":\"Europa\",\"fr\":\"Europe\",\"ja\":\"ヨーロッパ\",\"it\":\"Europa\",\"cn\":\"欧洲\",\"tr\":\"Avrupa\"}',5,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q46'),
	(21,'Micronesia','{\"kr\":\"오세아니아\",\"pt-BR\":\"Oceania\",\"pt\":\"Oceania\",\"nl\":\"Oceanië en Australië\",\"hr\":\"Óceánia és Ausztrália\",\"fa\":\"اقیانوسیه\",\"de\":\"Ozeanien und Australien\",\"es\":\"Oceanía\",\"fr\":\"Océanie\",\"ja\":\"オセアニア\",\"it\":\"Oceania\",\"cn\":\"大洋洲\",\"tr\":\"Okyanusya\"}',5,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q55643'),
  (22,'Polynesia','{\"kr\":\"유럽\",\"pt-BR\":\"Europa\",\"pt\":\"Europa\",\"nl\":\"Europa\",\"hr\":\"Európa\",\"fa\":\"اروپا\",\"de\":\"Europa\",\"es\":\"Europa\",\"fr\":\"Europe\",\"ja\":\"ヨーロッパ\",\"it\":\"Europa\",\"cn\":\"欧洲\",\"tr\":\"Avrupa\"}',5,'2023-08-14 07:11:03','2023-08-14 07:11:03',1,'Q46');



/*!40000 ALTER TABLE `regions` ENABLE KEYS */;
UNLOCK TABLES;

/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
