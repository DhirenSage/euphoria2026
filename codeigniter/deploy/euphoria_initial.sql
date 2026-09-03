/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `registration_id` bigint(20) unsigned NOT NULL,
  `event_id` bigint(20) unsigned NOT NULL,
  `event_day_id` bigint(20) unsigned NOT NULL,
  `gate_id` bigint(20) unsigned DEFAULT NULL,
  `scanner_user_id` bigint(20) unsigned DEFAULT NULL,
  `entry_time` datetime NOT NULL,
  `status` enum('allowed','duplicate','denied') NOT NULL DEFAULT 'allowed',
  `reason` varchar(180) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `daily_entry` (`event_id`,`registration_id`,`event_day_id`),
  KEY `attendance_registration` (`registration_id`),
  KEY `attendance_day` (`event_day_id`),
  KEY `attendance_event_time` (`event_id`,`entry_time`),
  KEY `fk_att_gate` (`gate_id`),
  KEY `fk_att_scanner` (`scanner_user_id`),
  CONSTRAINT `fk_att_day` FOREIGN KEY (`event_day_id`) REFERENCES `event_days` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_att_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_att_gate` FOREIGN KEY (`gate_id`) REFERENCES `gates` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_att_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_att_scanner` FOREIGN KEY (`scanner_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned DEFAULT NULL,
  `action` varchar(160) NOT NULL,
  `module` varchar(80) NOT NULL,
  `record_id` varchar(80) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `metadata_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metadata_json`)),
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `audit_action` (`action`),
  KEY `audit_created` (`created_at`),
  KEY `fk_audit_user` (`user_id`),
  CONSTRAINT `fk_audit_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `programme_id` bigint(20) unsigned NOT NULL,
  `name` varchar(160) NOT NULL,
  `slug` varchar(180) NOT NULL,
  `description` text DEFAULT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  `icon` varchar(80) DEFAULT NULL,
  `display_order` int(11) NOT NULL DEFAULT 0,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `category_slug` (`programme_id`,`slug`),
  KEY `category_programme` (`programme_id`),
  CONSTRAINT `fk_category_programme` FOREIGN KEY (`programme_id`) REFERENCES `programmes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES
(1,1,'Cultural','culture','A stage for the bold and expressive.',NULL,NULL,1,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(2,1,'Sports','sports','Play hard. Play fair. Play together.',NULL,NULL,4,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(3,1,'Hackathon','hackathon','Build the future before lunch.',NULL,NULL,3,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(4,1,'Technical','technical','Brains, bots and beautiful problems.',NULL,NULL,4,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(5,1,'Competitions','competitions','A little pressure makes great stories.',NULL,NULL,5,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(6,1,'Workshops','workshops','Learn something you can use tomorrow.',NULL,NULL,6,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(7,1,'Literary and Management','literary-and-management','Euphoria 2K26 registration category.',NULL,NULL,2,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(8,1,'Sci-Pha-Agro (The Magic of Science)','sci-pha-agro-the-magic-of-science','Euphoria 2K26 registration category.',NULL,NULL,3,1,'2026-09-03 07:47:30','2026-09-03 07:47:30');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
DROP TABLE IF EXISTS `coupon_usages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `coupon_usages` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `coupon_id` bigint(20) unsigned NOT NULL,
  `registration_id` bigint(20) unsigned NOT NULL,
  `discount_amount` decimal(10,2) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `coupon_registration` (`coupon_id`,`registration_id`),
  KEY `fk_cu_registration` (`registration_id`),
  CONSTRAINT `fk_cu_coupon` FOREIGN KEY (`coupon_id`) REFERENCES `coupons` (`id`),
  CONSTRAINT `fk_cu_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `coupon_usages` DISABLE KEYS */;
/*!40000 ALTER TABLE `coupon_usages` ENABLE KEYS */;
DROP TABLE IF EXISTS `coupons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `coupons` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(60) NOT NULL,
  `discount_type` enum('percent','fixed') NOT NULL,
  `discount_value` decimal(10,2) NOT NULL,
  `maximum_usage` int(11) DEFAULT NULL,
  `minimum_amount` decimal(10,2) NOT NULL DEFAULT 0.00,
  `starts_at` datetime DEFAULT NULL,
  `ends_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `coupons` DISABLE KEYS */;
/*!40000 ALTER TABLE `coupons` ENABLE KEYS */;
DROP TABLE IF EXISTS `email_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_jobs` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `registration_id` bigint(20) unsigned NOT NULL,
  `template_key` varchar(100) NOT NULL,
  `status` enum('pending','processing','sent','failed') NOT NULL DEFAULT 'pending',
  `attempts` smallint(6) NOT NULL DEFAULT 0,
  `available_at` datetime NOT NULL,
  `locked_at` datetime DEFAULT NULL,
  `last_error` text DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_registration_template` (`registration_id`,`template_key`),
  KEY `email_queue` (`status`,`available_at`),
  CONSTRAINT `fk_email_job_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `email_jobs` DISABLE KEYS */;
/*!40000 ALTER TABLE `email_jobs` ENABLE KEYS */;
DROP TABLE IF EXISTS `email_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_logs` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `registration_id` bigint(20) unsigned DEFAULT NULL,
  `recipient` varchar(190) NOT NULL,
  `template_key` varchar(100) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `status` enum('sent','failed') NOT NULL,
  `provider_reference` varchar(190) DEFAULT NULL,
  `error_message` text DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `email_log_registration` (`registration_id`),
  CONSTRAINT `fk_email_log_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `email_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `email_logs` ENABLE KEYS */;
DROP TABLE IF EXISTS `email_templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_templates` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `template_key` varchar(100) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `body_html` mediumtext NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `template_key` (`template_key`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `email_templates` DISABLE KEYS */;
INSERT INTO `email_templates` VALUES
(1,'event_pass','Euphoria 2026 – Your Event Registration is Confirmed','Your registration is confirmed. Please keep the attached QR pass ready at the entry gate.',1,'2026-09-03 07:47:30','2026-09-03 07:47:30');
/*!40000 ALTER TABLE `email_templates` ENABLE KEYS */;
DROP TABLE IF EXISTS `event_days`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_days` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `event_id` bigint(20) unsigned NOT NULL,
  `label` varchar(80) NOT NULL,
  `event_date` date NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `event_day` (`event_id`,`event_date`),
  CONSTRAINT `fk_day_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=112 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `event_days` DISABLE KEYS */;
INSERT INTO `event_days` VALUES
(1,1,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(2,1,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(3,1,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(4,2,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(5,2,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(6,2,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(7,3,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(8,3,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(9,3,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(10,4,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(11,4,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(12,4,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(13,5,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(14,5,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(15,5,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(16,6,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(17,6,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(18,6,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(19,7,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(20,7,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(21,7,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(22,8,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(23,8,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(24,8,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(25,9,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(26,9,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(27,9,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(28,10,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(29,10,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(30,10,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(31,11,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(32,11,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(33,11,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(34,12,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(35,12,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(36,12,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(37,13,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(38,13,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(39,13,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(40,14,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(41,14,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(42,14,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(43,15,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(44,15,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(45,15,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(46,16,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(47,16,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(48,16,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(49,17,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(50,17,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(51,17,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(52,18,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(53,18,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(54,18,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(55,19,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(56,19,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(57,19,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(58,20,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(59,20,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(60,20,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(61,21,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(62,21,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(63,21,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(64,22,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(65,22,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(66,22,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(67,23,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(68,23,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(69,23,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(70,24,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(71,24,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(72,24,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(73,25,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(74,25,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(75,25,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(76,26,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(77,26,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(78,26,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(79,27,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(80,27,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(81,27,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(82,28,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(83,28,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(84,28,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(85,29,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(86,29,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(87,29,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(88,30,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(89,30,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(90,30,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(91,31,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(92,31,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(93,31,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(94,32,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(95,32,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(96,32,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(97,33,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(98,33,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(99,33,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(100,34,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(101,34,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(102,34,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(103,35,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(104,35,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(105,35,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(106,36,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(107,36,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(108,36,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(109,37,'Day 1','2026-09-15',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(110,37,'Day 2','2026-09-16',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(111,37,'Day 3','2026-09-17',1,'2026-09-03 07:47:30','2026-09-03 07:47:30');
/*!40000 ALTER TABLE `event_days` ENABLE KEYS */;
DROP TABLE IF EXISTS `event_galleries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_galleries` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `event_id` bigint(20) unsigned NOT NULL,
  `album` varchar(140) DEFAULT NULL,
  `image_path` varchar(255) NOT NULL,
  `caption` varchar(255) DEFAULT NULL,
  `event_date` date DEFAULT NULL,
  `display_order` int(11) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gallery_event` (`event_id`,`display_order`),
  CONSTRAINT `fk_gallery_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `event_galleries` DISABLE KEYS */;
/*!40000 ALTER TABLE `event_galleries` ENABLE KEYS */;
DROP TABLE IF EXISTS `event_schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_schedules` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `event_id` bigint(20) unsigned NOT NULL,
  `event_day_id` bigint(20) unsigned DEFAULT NULL,
  `title` varchar(180) NOT NULL,
  `starts_at` datetime NOT NULL,
  `ends_at` datetime DEFAULT NULL,
  `venue` varchar(180) DEFAULT NULL,
  `display_order` int(11) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `schedule_event` (`event_id`,`starts_at`),
  KEY `fk_schedule_day` (`event_day_id`),
  CONSTRAINT `fk_schedule_day` FOREIGN KEY (`event_day_id`) REFERENCES `event_days` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_schedule_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `event_schedules` DISABLE KEYS */;
/*!40000 ALTER TABLE `event_schedules` ENABLE KEYS */;
DROP TABLE IF EXISTS `event_speakers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_speakers` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `event_id` bigint(20) unsigned NOT NULL,
  `name` varchar(160) NOT NULL,
  `designation` varchar(160) DEFAULT NULL,
  `organization` varchar(180) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `role` varchar(60) DEFAULT NULL,
  `photo_path` varchar(255) DEFAULT NULL,
  `display_order` int(11) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_speaker_event` (`event_id`),
  CONSTRAINT `fk_speaker_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `event_speakers` DISABLE KEYS */;
/*!40000 ALTER TABLE `event_speakers` ENABLE KEYS */;
DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `events` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `category_id` bigint(20) unsigned NOT NULL,
  `name` varchar(180) NOT NULL,
  `slug` varchar(200) NOT NULL,
  `short_description` varchar(300) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `banner_path` varchar(255) DEFAULT NULL,
  `thumbnail_path` varchar(255) DEFAULT NULL,
  `event_type` enum('competition','workshop','sports','hackathon','quiz','other') NOT NULL DEFAULT 'competition',
  `registration_type` enum('individual','team','both') NOT NULL DEFAULT 'individual',
  `fee` decimal(10,2) NOT NULL DEFAULT 0.00,
  `payment_required` tinyint(1) NOT NULL DEFAULT 1,
  `tax_amount` decimal(10,2) NOT NULL DEFAULT 0.00,
  `discount_amount` decimal(10,2) NOT NULL DEFAULT 0.00,
  `capacity` int(11) NOT NULL DEFAULT 0,
  `min_team_size` int(11) DEFAULT NULL,
  `max_team_size` int(11) DEFAULT NULL,
  `registration_start` datetime DEFAULT NULL,
  `registration_end` datetime DEFAULT NULL,
  `event_start` datetime DEFAULT NULL,
  `event_end` datetime DEFAULT NULL,
  `venue` varchar(180) DEFAULT NULL,
  `eligibility` varchar(255) DEFAULT NULL,
  `rules` text DEFAULT NULL,
  `prizes` text DEFAULT NULL,
  `refund_policy` text DEFAULT NULL,
  `contact_details` varchar(255) DEFAULT NULL,
  `status` enum('draft','scheduled','registration_open','registration_closed','full','live','completed','cancelled','archived') NOT NULL DEFAULT 'draft',
  `is_featured` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  UNIQUE KEY `event_slug` (`slug`),
  KEY `event_category_status` (`category_id`,`status`),
  CONSTRAINT `fk_event_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES
(1,1,'Dance Competition','dance-competition','The floor is yours.','A high-energy Euphoria experience designed for students who want to participate, not just watch.',NULL,NULL,'competition','individual',500.00,1,0.00,0.00,200,NULL,NULL,NULL,NULL,'2026-09-15 10:00:00','2026-09-17 18:00:00','Main auditorium',NULL,NULL,NULL,NULL,NULL,'archived',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(2,1,'Battle of Bands','battle-of-bands','Step into Battle of Bands and make your EUPHORIA 2K26 moment count.','Battle of Bands is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','team',2499.00,1,0.00,0.00,250,3,12,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Main Auditorium · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(3,2,'Cricket','cricket','Step into Cricket and make your EUPHORIA 2K26 moment count.','Cricket is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','team',1600.00,1,0.00,0.00,250,11,15,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(4,2,'Football','football','Step into Football and make your EUPHORIA 2K26 moment count.','Football is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','team',1000.00,1,0.00,0.00,250,7,14,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(5,2,'Chess','chess','Step into Chess and make your EUPHORIA 2K26 moment count.','Chess is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','individual',200.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(6,3,'AI Hackathon','ai-hackathon','Ship a sharp idea with your team.','A high-energy Euphoria experience designed for students who want to participate, not just watch.',NULL,NULL,'hackathon','team',500.00,1,0.00,0.00,200,NULL,NULL,NULL,NULL,'2026-09-15 10:00:00','2026-09-17 18:00:00','Innovation lab',NULL,NULL,NULL,NULL,NULL,'registration_open',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(7,4,'Coding Challenge','coding-challenge','Think fast. Write clean.','A high-energy Euphoria experience designed for students who want to participate, not just watch.',NULL,NULL,'competition','individual',100.00,1,0.00,0.00,200,NULL,NULL,NULL,NULL,'2026-09-15 10:00:00','2026-09-17 18:00:00','Computer centre',NULL,NULL,NULL,NULL,NULL,'scheduled',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(8,4,'Quiz','quiz','The buzzer is waiting.','A high-energy Euphoria experience designed for students who want to participate, not just watch.',NULL,NULL,'quiz','individual',100.00,1,0.00,0.00,200,NULL,NULL,NULL,NULL,'2026-09-15 10:00:00','2026-09-17 18:00:00','Block A auditorium',NULL,NULL,NULL,NULL,NULL,'registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(9,6,'Campus Photography Walk','photography-walk','Frame the campus your way.','A high-energy Euphoria experience designed for students who want to participate, not just watch.',NULL,NULL,'workshop','individual',0.00,0,0.00,0.00,200,NULL,NULL,NULL,NULL,'2026-09-15 10:00:00','2026-09-17 18:00:00','Central lawn',NULL,NULL,NULL,NULL,NULL,'registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(10,1,'Move & Groove (Solo Dance Competition)','move-groove-solo-dance','Step into Move & Groove (Solo Dance Competition) and make your EUPHORIA 2K26 moment count.','Move & Groove (Solo Dance Competition) is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',299.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Main Auditorium · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(11,1,'Move & Groove (Group Dance Competition)','move-groove-group-dance','Step into Move & Groove (Group Dance Competition) and make your EUPHORIA 2K26 moment count.','Move & Groove (Group Dance Competition) is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','team',899.00,1,0.00,0.00,250,2,20,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Main Auditorium · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(12,1,'Swar Fiesta (Solo Singing Competition)','swar-fiesta-solo-singing','Step into Swar Fiesta (Solo Singing Competition) and make your EUPHORIA 2K26 moment count.','Swar Fiesta (Solo Singing Competition) is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',299.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Main Auditorium · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(13,1,'Rap Battle','rap-battle','Step into Rap Battle and make your EUPHORIA 2K26 moment count.','Rap Battle is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',249.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Main Auditorium · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(14,1,'Fashion-Fiesta (Fashion Show – Solo Model Round)','fashion-fiesta-solo-model','Step into Fashion-Fiesta (Fashion Show – Solo Model Round) and make your EUPHORIA 2K26 moment count.','Fashion-Fiesta (Fashion Show – Solo Model Round) is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',799.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Main Auditorium · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(15,1,'Fashion-Fiesta (Designer Round – Min 4 Garments)','fashion-fiesta-designer-round','Step into Fashion-Fiesta (Designer Round – Min 4 Garments) and make your EUPHORIA 2K26 moment count.','Fashion-Fiesta (Designer Round – Min 4 Garments) is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',2499.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Main Auditorium · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(16,1,'Model Hunt (Audition)','model-hunt-audition','Step into Model Hunt (Audition) and make your EUPHORIA 2K26 moment count.','Model Hunt (Audition) is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',199.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Main Auditorium · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(17,1,'Game Mania','game-mania','Step into Game Mania and make your EUPHORIA 2K26 moment count.','Game Mania is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',99.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Main Auditorium · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(18,1,'Reel Making Competition','reel-making-competition','Step into Reel Making Competition and make your EUPHORIA 2K26 moment count.','Reel Making Competition is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',199.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Main Auditorium · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(19,7,'Crack the Clue (Treasure Hunt)','crack-the-clue-treasure-hunt','Step into Crack the Clue (Treasure Hunt) and make your EUPHORIA 2K26 moment count.','Crack the Clue (Treasure Hunt) is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','team',999.00,1,0.00,0.00,250,2,6,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Seminar Hall · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(20,7,'Bid To Win (IPL Auction)','bid-to-win-ipl-auction','Step into Bid To Win (IPL Auction) and make your EUPHORIA 2K26 moment count.','Bid To Win (IPL Auction) is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','team',499.00,1,0.00,0.00,250,2,5,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Seminar Hall · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(21,7,'The Great Debate','the-great-debate','Step into The Great Debate and make your EUPHORIA 2K26 moment count.','The Great Debate is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',249.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Seminar Hall · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(22,7,'Vocal Ink (Slam Poetry)','vocal-ink-slam-poetry','Step into Vocal Ink (Slam Poetry) and make your EUPHORIA 2K26 moment count.','Vocal Ink (Slam Poetry) is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',249.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Seminar Hall · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(23,8,'Model/Product Making Presentation','model-product-making-presentation','Step into Model/Product Making Presentation and make your EUPHORIA 2K26 moment count.','Model/Product Making Presentation is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',249.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Seminar Hall · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(24,8,'Oral / Poster Presentation','oral-poster-presentation','Step into Oral / Poster Presentation and make your EUPHORIA 2K26 moment count.','Oral / Poster Presentation is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',249.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Seminar Hall · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(25,8,'On Spot / Attending','on-spot-attending','Step into On Spot / Attending and make your EUPHORIA 2K26 moment count.','On Spot / Attending is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'competition','individual',299.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','Seminar Hall · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(26,2,'Basketball','basketball','Step into Basketball and make your EUPHORIA 2K26 moment count.','Basketball is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','team',1000.00,1,0.00,0.00,250,5,12,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(27,2,'Kabaddi','kabaddi','Step into Kabaddi and make your EUPHORIA 2K26 moment count.','Kabaddi is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','team',800.00,1,0.00,0.00,250,7,12,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(28,2,'Carrom','carrom','Step into Carrom and make your EUPHORIA 2K26 moment count.','Carrom is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','individual',200.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(29,2,'Volleyball','volleyball','Step into Volleyball and make your EUPHORIA 2K26 moment count.','Volleyball is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','team',800.00,1,0.00,0.00,250,6,12,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(30,2,'Table Tennis','table-tennis','Step into Table Tennis and make your EUPHORIA 2K26 moment count.','Table Tennis is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','individual',250.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(31,2,'Badminton (Singles) Men','badminton-singles-men','Step into Badminton (Singles) Men and make your EUPHORIA 2K26 moment count.','Badminton (Singles) Men is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','individual',300.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(32,2,'Badminton (Doubles) Men','badminton-doubles-men','Step into Badminton (Doubles) Men and make your EUPHORIA 2K26 moment count.','Badminton (Doubles) Men is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','team',400.00,1,0.00,0.00,250,2,2,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(33,2,'Badminton (Singles) Women','badminton-singles-women','Step into Badminton (Singles) Women and make your EUPHORIA 2K26 moment count.','Badminton (Singles) Women is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','individual',200.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(34,2,'Badminton (Doubles) Women','badminton-doubles-women','Step into Badminton (Doubles) Women and make your EUPHORIA 2K26 moment count.','Badminton (Doubles) Women is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','team',400.00,1,0.00,0.00,250,2,2,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(35,2,'Power Lifting','power-lifting','Step into Power Lifting and make your EUPHORIA 2K26 moment count.','Power Lifting is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','individual',300.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(36,2,'Weight Lifting','weight-lifting','Step into Weight Lifting and make your EUPHORIA 2K26 moment count.','Weight Lifting is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','individual',300.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(37,2,'Arm Wrestling','arm-wrestling','Step into Arm Wrestling and make your EUPHORIA 2K26 moment count.','Arm Wrestling is an official EUPHORIA 2K26 event at SAGE University Indore. It brings students together to compete, perform and learn in a professionally coordinated festival environment.',NULL,NULL,'sports','individual',150.00,1,0.00,0.00,250,NULL,NULL,'2026-01-01 00:00:00','2026-09-14 23:59:59','2026-09-15 10:00:00','2026-09-17 18:00:00','University Sports Complex · SAGE University Indore','Open to school and college students with a valid institutional ID.','Carry registration confirmation and photo ID. Report 30 minutes early. Follow coordinator and safety instructions. The organising committee decision is final.','Winner trophy and merit certificate. Runner-up merit certificate. Participation certificate for eligible participants.',NULL,'EUPHORIA Event Desk · SAGE University Indore','registration_open',0,'2026-09-03 07:47:30','2026-09-03 07:47:30');
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
DROP TABLE IF EXISTS `gates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `gates` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `programme_id` bigint(20) unsigned NOT NULL,
  `name` varchar(100) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_gate_programme` (`programme_id`),
  CONSTRAINT `fk_gate_programme` FOREIGN KEY (`programme_id`) REFERENCES `programmes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `gates` DISABLE KEYS */;
INSERT INTO `gates` VALUES
(1,1,'Gate 1 · Main Entry',1,'2026-09-03 07:47:30','2026-09-03 07:47:30');
/*!40000 ALTER TABLE `gates` ENABLE KEYS */;
DROP TABLE IF EXISTS `migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `migrations` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `version` varchar(255) NOT NULL,
  `class` varchar(255) NOT NULL,
  `group` varchar(255) NOT NULL,
  `namespace` varchar(255) NOT NULL,
  `time` int(11) NOT NULL,
  `batch` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `migrations` DISABLE KEYS */;
INSERT INTO `migrations` VALUES
(1,'2026-01-01-000001','App\\Database\\Migrations\\CreatePlatformTables','default','App',1788421650,1),
(2,'2026-01-01-000002','App\\Database\\Migrations\\ExtendOperationalTables','default','App',1788421650,1),
(3,'2026-01-01-000003','App\\Database\\Migrations\\AddLegacyRegistrationProfileFields','default','App',1788421650,1),
(4,'2026-01-01-000004','App\\Database\\Migrations\\CompleteCoreWorkflow','default','App',1788421650,1);
/*!40000 ALTER TABLE `migrations` ENABLE KEYS */;
DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned DEFAULT NULL,
  `channel` varchar(40) NOT NULL,
  `title` varchar(180) NOT NULL,
  `body` text NOT NULL,
  `read_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notification_user` (`user_id`,`read_at`),
  CONSTRAINT `fk_notification_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
DROP TABLE IF EXISTS `payment_transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment_transactions` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `payment_id` bigint(20) unsigned NOT NULL,
  `action` varchar(60) NOT NULL,
  `gateway_reference` varchar(160) DEFAULT NULL,
  `status` varchar(60) NOT NULL,
  `response_digest` char(64) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `pt_payment` (`payment_id`,`created_at`),
  CONSTRAINT `fk_pt_payment` FOREIGN KEY (`payment_id`) REFERENCES `payments` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `payment_transactions` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_transactions` ENABLE KEYS */;
DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `registration_id` bigint(20) unsigned NOT NULL,
  `txnid` varchar(80) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `productinfo` varchar(100) NOT NULL DEFAULT 'euphoria2026',
  `gateway` varchar(40) NOT NULL DEFAULT 'easebuzz',
  `gateway_order_id` varchar(120) DEFAULT NULL,
  `gateway_payment_id` varchar(120) DEFAULT NULL,
  `status` enum('created','pending','initiated','success','failed','cancelled','refunded','unknown') NOT NULL DEFAULT 'created',
  `raw_reference` text DEFAULT NULL,
  `paid_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `txnid` (`txnid`),
  KEY `payment_status` (`status`),
  KEY `fk_payment_registration` (`registration_id`),
  CONSTRAINT `fk_payment_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES
(1,'events.view','Events View'),
(2,'events.create','Events Create'),
(3,'events.edit','Events Edit'),
(4,'events.delete','Events Delete'),
(5,'registrations.view','Registrations View'),
(6,'registrations.edit','Registrations Edit'),
(7,'payments.view','Payments View'),
(8,'payments.verify','Payments Verify'),
(9,'attendance.view','Attendance View'),
(10,'attendance.scan','Attendance Scan'),
(11,'reports.export','Reports Export'),
(12,'users.manage','Users Manage');
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
DROP TABLE IF EXISTS `programmes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `programmes` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(160) NOT NULL,
  `slug` varchar(180) NOT NULL,
  `year` smallint(6) NOT NULL,
  `description` text DEFAULT NULL,
  `status` enum('draft','published','archived') NOT NULL DEFAULT 'draft',
  `starts_on` date DEFAULT NULL,
  `ends_on` date DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `programmes` DISABLE KEYS */;
INSERT INTO `programmes` VALUES
(1,'Euphoria 2026','euphoria-2026',2026,'A multi-day student festival at SAGE University Indore.','published','2026-09-15','2026-09-17','2026-09-03 07:47:30','2026-09-03 07:47:30');
/*!40000 ALTER TABLE `programmes` ENABLE KEYS */;
DROP TABLE IF EXISTS `qr_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `qr_tokens` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `registration_id` bigint(20) unsigned NOT NULL,
  `token_hash` char(64) NOT NULL,
  `token_hint` varchar(20) NOT NULL,
  `token_ciphertext` text DEFAULT NULL,
  `status` enum('active','revoked','expired') NOT NULL DEFAULT 'active',
  `created_at` datetime NOT NULL,
  `revoked_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `registration_id` (`registration_id`),
  UNIQUE KEY `token_hash` (`token_hash`),
  CONSTRAINT `fk_qr_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `qr_tokens` DISABLE KEYS */;
/*!40000 ALTER TABLE `qr_tokens` ENABLE KEYS */;
DROP TABLE IF EXISTS `registration_field_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration_field_values` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `registration_id` bigint(20) unsigned NOT NULL,
  `field_id` bigint(20) unsigned NOT NULL,
  `value_text` text DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `registration_field` (`registration_id`,`field_id`),
  KEY `fk_rfv_field` (`field_id`),
  CONSTRAINT `fk_rfv_field` FOREIGN KEY (`field_id`) REFERENCES `registration_fields` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_rfv_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `registration_field_values` DISABLE KEYS */;
/*!40000 ALTER TABLE `registration_field_values` ENABLE KEYS */;
DROP TABLE IF EXISTS `registration_fields`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration_fields` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `event_id` bigint(20) unsigned NOT NULL,
  `label` varchar(160) NOT NULL,
  `field_name` varchar(100) NOT NULL,
  `field_type` enum('text','number','email','phone','date','select','radio','checkbox','textarea','file') NOT NULL DEFAULT 'text',
  `placeholder` varchar(180) DEFAULT NULL,
  `options_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`options_json`)),
  `is_required` tinyint(1) NOT NULL DEFAULT 0,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `display_order` int(11) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `event_field_name` (`event_id`,`field_name`),
  CONSTRAINT `fk_field_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `registration_fields` DISABLE KEYS */;
INSERT INTO `registration_fields` VALUES
(1,1,'Full name','participant_name','text',NULL,NULL,1,0,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(2,1,'Email address','email','email',NULL,NULL,1,0,2,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(3,1,'Mobile number','mobile','phone',NULL,NULL,1,0,3,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(4,1,'College / institution','college','text',NULL,NULL,0,0,4,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(5,2,'Full name','participant_name','text',NULL,NULL,1,0,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(6,2,'Email address','email','email',NULL,NULL,1,0,2,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(7,2,'Mobile number','mobile','phone',NULL,NULL,1,0,3,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(8,2,'College / institution','college','text',NULL,NULL,0,0,4,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(9,3,'Full name','participant_name','text',NULL,NULL,1,0,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(10,3,'Email address','email','email',NULL,NULL,1,0,2,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(11,3,'Mobile number','mobile','phone',NULL,NULL,1,0,3,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(12,3,'College / institution','college','text',NULL,NULL,0,0,4,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(13,4,'Full name','participant_name','text',NULL,NULL,1,0,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(14,4,'Email address','email','email',NULL,NULL,1,0,2,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(15,4,'Mobile number','mobile','phone',NULL,NULL,1,0,3,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(16,4,'College / institution','college','text',NULL,NULL,0,0,4,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(17,5,'Full name','participant_name','text',NULL,NULL,1,0,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(18,5,'Email address','email','email',NULL,NULL,1,0,2,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(19,5,'Mobile number','mobile','phone',NULL,NULL,1,0,3,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(20,5,'College / institution','college','text',NULL,NULL,0,0,4,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(21,6,'Full name','participant_name','text',NULL,NULL,1,0,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(22,6,'Email address','email','email',NULL,NULL,1,0,2,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(23,6,'Mobile number','mobile','phone',NULL,NULL,1,0,3,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(24,6,'College / institution','college','text',NULL,NULL,0,0,4,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(25,7,'Full name','participant_name','text',NULL,NULL,1,0,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(26,7,'Email address','email','email',NULL,NULL,1,0,2,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(27,7,'Mobile number','mobile','phone',NULL,NULL,1,0,3,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(28,7,'College / institution','college','text',NULL,NULL,0,0,4,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(29,8,'Full name','participant_name','text',NULL,NULL,1,0,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(30,8,'Email address','email','email',NULL,NULL,1,0,2,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(31,8,'Mobile number','mobile','phone',NULL,NULL,1,0,3,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(32,8,'College / institution','college','text',NULL,NULL,0,0,4,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(33,9,'Full name','participant_name','text',NULL,NULL,1,0,1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(34,9,'Email address','email','email',NULL,NULL,1,0,2,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(35,9,'Mobile number','mobile','phone',NULL,NULL,1,0,3,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(36,9,'College / institution','college','text',NULL,NULL,0,0,4,'2026-09-03 07:47:30','2026-09-03 07:47:30');
/*!40000 ALTER TABLE `registration_fields` ENABLE KEYS */;
DROP TABLE IF EXISTS `registration_forms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration_forms` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `event_id` bigint(20) unsigned NOT NULL,
  `title` varchar(180) NOT NULL,
  `instructions` text DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `event_id` (`event_id`),
  CONSTRAINT `fk_form_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `registration_forms` DISABLE KEYS */;
/*!40000 ALTER TABLE `registration_forms` ENABLE KEYS */;
DROP TABLE IF EXISTS `registration_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration_members` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `registration_id` bigint(20) unsigned NOT NULL,
  `name` varchar(160) NOT NULL,
  `email` varchar(190) DEFAULT NULL,
  `mobile` varchar(30) DEFAULT NULL,
  `college` varchar(180) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_member_registration` (`registration_id`),
  CONSTRAINT `fk_member_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `registration_members` DISABLE KEYS */;
/*!40000 ALTER TABLE `registration_members` ENABLE KEYS */;
DROP TABLE IF EXISTS `registration_sequences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration_sequences` (
  `sequence_key` varchar(80) NOT NULL,
  `next_value` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`sequence_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `registration_sequences` DISABLE KEYS */;
/*!40000 ALTER TABLE `registration_sequences` ENABLE KEYS */;
DROP TABLE IF EXISTS `registrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `registrations` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `event_id` bigint(20) unsigned NOT NULL,
  `registration_id` varchar(60) NOT NULL,
  `participant_name` varchar(160) NOT NULL,
  `father_name` varchar(160) DEFAULT NULL,
  `email` varchar(190) NOT NULL,
  `mobile` varchar(30) NOT NULL,
  `age` tinyint(3) unsigned DEFAULT NULL,
  `college` varchar(180) DEFAULT NULL,
  `city` varchar(120) DEFAULT NULL,
  `participant_affiliation` enum('sageian','non_sageian') NOT NULL DEFAULT 'non_sageian',
  `registration_type` enum('individual','team') NOT NULL DEFAULT 'individual',
  `team_name` varchar(160) DEFAULT NULL,
  `total_amount` decimal(10,2) NOT NULL DEFAULT 0.00,
  `status` enum('pending_payment','confirmed','cancelled','rejected','completed') NOT NULL DEFAULT 'pending_payment',
  `qr_status` enum('active','suspended','cancelled','expired') NOT NULL DEFAULT 'active',
  `pass_access_hash` char(64) DEFAULT NULL,
  `pass_access_ciphertext` text DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `registration_id` (`registration_id`),
  UNIQUE KEY `registration_pass_access` (`pass_access_hash`),
  KEY `registration_event` (`event_id`),
  KEY `registration_email` (`email`),
  KEY `registration_affiliation` (`participant_affiliation`),
  CONSTRAINT `fk_registration_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `registrations` DISABLE KEYS */;
/*!40000 ALTER TABLE `registrations` ENABLE KEYS */;
DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permissions` (
  `role_id` bigint(20) unsigned NOT NULL,
  `permission_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`role_id`,`permission_id`),
  KEY `fk_rp_permission` (`permission_id`),
  CONSTRAINT `fk_rp_permission` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_rp_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `role_permissions` ENABLE KEYS */;
DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES
(6,'CONTENT_MANAGER'),
(3,'EVENT_ADMIN'),
(4,'FINANCE'),
(2,'PROGRAMME_ADMIN'),
(7,'REPORT_VIEWER'),
(5,'SCANNER'),
(1,'SUPER_ADMIN');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
DROP TABLE IF EXISTS `scan_attempts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `scan_attempts` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `registration_id` bigint(20) unsigned DEFAULT NULL,
  `event_id` bigint(20) unsigned DEFAULT NULL,
  `event_day_id` bigint(20) unsigned DEFAULT NULL,
  `gate_id` bigint(20) unsigned DEFAULT NULL,
  `scanner_user_id` bigint(20) unsigned DEFAULT NULL,
  `token_hint` varchar(20) DEFAULT NULL,
  `status` enum('allowed','duplicate','denied') NOT NULL,
  `reason` varchar(255) NOT NULL,
  `attempted_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `scan_attempt_status_time` (`status`,`attempted_at`),
  KEY `scan_attempt_event` (`event_id`,`event_day_id`),
  KEY `fk_scan_attempt_registration` (`registration_id`),
  KEY `fk_scan_attempt_day` (`event_day_id`),
  KEY `fk_scan_attempt_gate` (`gate_id`),
  KEY `fk_scan_attempt_scanner` (`scanner_user_id`),
  CONSTRAINT `fk_scan_attempt_day` FOREIGN KEY (`event_day_id`) REFERENCES `event_days` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_scan_attempt_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_scan_attempt_gate` FOREIGN KEY (`gate_id`) REFERENCES `gates` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_scan_attempt_registration` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_scan_attempt_scanner` FOREIGN KEY (`scanner_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `scan_attempts` DISABLE KEYS */;
/*!40000 ALTER TABLE `scan_attempts` ENABLE KEYS */;
DROP TABLE IF EXISTS `scanner_assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `scanner_assignments` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL,
  `event_id` bigint(20) unsigned NOT NULL,
  `event_day_id` bigint(20) unsigned NOT NULL,
  `gate_id` bigint(20) unsigned NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `scanner_scope` (`user_id`,`event_id`,`event_day_id`,`gate_id`),
  KEY `fk_sa_event` (`event_id`),
  KEY `fk_sa_day` (`event_day_id`),
  KEY `fk_sa_gate` (`gate_id`),
  CONSTRAINT `fk_sa_day` FOREIGN KEY (`event_day_id`) REFERENCES `event_days` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sa_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sa_gate` FOREIGN KEY (`gate_id`) REFERENCES `gates` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sa_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `scanner_assignments` DISABLE KEYS */;
INSERT INTO `scanner_assignments` VALUES
(1,2,1,1,1,1,'2026-09-03 07:47:30');
/*!40000 ALTER TABLE `scanner_assignments` ENABLE KEYS */;
DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `settings` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(120) NOT NULL,
  `setting_value` text DEFAULT NULL,
  `is_secret` tinyint(1) NOT NULL DEFAULT 0,
  `updated_by` bigint(20) unsigned DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `setting_key` (`setting_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
DROP TABLE IF EXISTS `uploaded_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `uploaded_files` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned DEFAULT NULL,
  `module` varchar(60) NOT NULL,
  `record_id` varchar(80) DEFAULT NULL,
  `original_name` varchar(255) NOT NULL,
  `storage_path` varchar(255) NOT NULL,
  `mime_type` varchar(120) NOT NULL,
  `size_bytes` bigint(20) unsigned NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `storage_path` (`storage_path`),
  KEY `fk_upload_user` (`user_id`),
  CONSTRAINT `fk_upload_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `uploaded_files` DISABLE KEYS */;
/*!40000 ALTER TABLE `uploaded_files` ENABLE KEYS */;
DROP TABLE IF EXISTS `user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_roles` (
  `user_id` bigint(20) unsigned NOT NULL,
  `role_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `fk_ur_role` (`role_id`),
  CONSTRAINT `fk_ur_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ur_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `user_roles` DISABLE KEYS */;
INSERT INTO `user_roles` VALUES
(1,1),
(2,5);
/*!40000 ALTER TABLE `user_roles` ENABLE KEYS */;
DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(160) NOT NULL,
  `email` varchar(190) NOT NULL,
  `phone` varchar(30) DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES
(1,'Euphoria Demo Admin','admin@euphoria.test',NULL,'$2y$10$xmXMj6smFblAuDdPIYVqs.crx4a5D4JscdQ0MlvEJcc4bzveRYCei',1,'2026-09-03 07:47:30','2026-09-03 07:47:30'),
(2,'Gate One Scanner','scanner@euphoria.test',NULL,'$2y$10$kd02bmCN0CRRKztHOHe32e.Oxkf33SB2CHsPp/CHb.jyA91BZjkvC',1,'2026-09-03 07:47:30','2026-09-03 07:47:30');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

