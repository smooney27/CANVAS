-- MySQL dump 10.13  Distrib 5.1.42, for apple-darwin9.5.0 (i386)
--
-- Host: localhost    Database: streetview
-- ------------------------------------------------------
-- Server version	5.1.42

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
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_bda51c3c` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_message`
--

DROP TABLE IF EXISTS `auth_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_message_fbfc09f1` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_message`
--

LOCK TABLES `auth_message` WRITE;
/*!40000 ALTER TABLE `auth_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_e4470c6e` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=64 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add message',4,'add_message'),(11,'Can change message',4,'change_message'),(12,'Can delete message',4,'delete_message'),(13,'Can add content type',5,'add_contenttype'),(14,'Can change content type',5,'change_contenttype'),(15,'Can delete content type',5,'delete_contenttype'),(16,'Can add session',6,'add_session'),(17,'Can change session',6,'change_session'),(18,'Can delete session',6,'delete_session'),(19,'Can add site',7,'add_site'),(20,'Can change site',7,'change_site'),(21,'Can delete site',7,'delete_site'),(22,'Can add log entry',8,'add_logentry'),(23,'Can change log entry',8,'change_logentry'),(24,'Can delete log entry',8,'delete_logentry'),(25,'Can add rating type',9,'add_ratingtype'),(26,'Can change rating type',9,'change_ratingtype'),(27,'Can delete rating type',9,'delete_ratingtype'),(28,'Can add category',10,'add_category'),(29,'Can change category',10,'change_category'),(30,'Can delete category',10,'delete_category'),(31,'Can add item',11,'add_item'),(32,'Can change item',11,'change_item'),(33,'Can delete item',11,'delete_item'),(34,'Can add module',12,'add_module'),(35,'Can change module',12,'change_module'),(36,'Can delete module',12,'delete_module'),(37,'Can add project',13,'add_project'),(38,'Can change project',13,'change_project'),(39,'Can delete project',13,'delete_project'),(40,'Can add study',14,'add_study'),(41,'Can change study',14,'change_study'),(42,'Can delete study',14,'delete_study'),(43,'Can add segment',15,'add_segment'),(44,'Can change segment',15,'change_segment'),(45,'Can delete segment',15,'delete_segment'),(46,'Can add step',16,'add_step'),(47,'Can change step',16,'change_step'),(48,'Can delete step',16,'delete_step'),(49,'Can add boolean rating',17,'add_booleanrating'),(50,'Can change boolean rating',17,'change_booleanrating'),(51,'Can delete boolean rating',17,'delete_booleanrating'),(52,'Can add category rating',18,'add_categoryrating'),(53,'Can change category rating',18,'change_categoryrating'),(54,'Can delete category rating',18,'delete_categoryrating'),(55,'Can add count rating',19,'add_countrating'),(56,'Can change count rating',19,'change_countrating'),(57,'Can delete count rating',19,'delete_countrating'),(58,'Can add free form rating',20,'add_freeformrating'),(59,'Can change free form rating',20,'change_freeformrating'),(60,'Can delete free form rating',20,'delete_freeformrating'),(61,'Can add rating task',21,'add_ratingtask'),(62,'Can change rating task',21,'change_ratingtask'),(63,'Can delete rating task',21,'delete_ratingtask');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'smooney','','','smooney27@gmail.com','sha1$94e54$d90bf2ddf1c320c4d13e88f3a9951358604431f0',1,1,1,'2011-01-19 16:51:57','2011-01-19 16:45:31'),(2,'rater','','','','sha1$3955e$6aa4f90f5daf1f87b4385002bbc6c6a83fb5f459',0,1,0,'2011-01-20 11:04:11','2011-01-20 11:04:11');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_fbfc09f1` (`user_id`),
  KEY `auth_user_groups_bda51c3c` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_fbfc09f1` (`user_id`),
  KEY `auth_user_user_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_fbfc09f1` (`user_id`),
  KEY `django_admin_log_e4470c6e` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=20 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2011-01-19 16:52:21',1,13,'1','Project object',1,''),(2,'2011-01-19 16:58:30',1,13,'2','Project object',1,''),(3,'2011-01-19 17:01:38',1,13,'2','Project object',2,'Changed name.'),(4,'2011-01-20 10:12:18',1,13,'1','Project object',1,''),(5,'2011-01-20 10:50:30',1,11,'1','Item object',1,''),(6,'2011-01-20 10:55:32',1,11,'1','Paved',2,'No fields changed.'),(7,'2011-01-20 10:58:52',1,12,'1','Test Module',1,''),(8,'2011-01-20 10:58:55',1,14,'1','My test project\'s study',1,''),(9,'2011-01-20 11:03:18',1,15,'1','(-85.585406,33.834390)->(-85.585332,33.838537)',1,''),(10,'2011-01-20 11:04:11',1,3,'2','rater',1,''),(11,'2011-01-20 11:04:33',1,3,'2','rater',2,'No fields changed.'),(12,'2011-01-20 11:14:42',1,13,'1','Test',2,'Changed managers and raters.'),(13,'2011-01-20 11:20:13',1,21,'1','RatingTask object',1,''),(14,'2011-01-20 11:37:46',1,9,'1','boolean rating type',1,''),(15,'2011-01-20 11:38:07',1,11,'1','Paved',1,''),(16,'2011-01-20 11:38:22',1,12,'1','Test Module',1,''),(17,'2011-01-20 11:38:49',1,13,'1','Simple Test Project',1,''),(18,'2011-01-20 11:39:12',1,14,'1','Simple Test Study',1,''),(19,'2011-01-20 11:39:49',1,15,'1','(-85.585406,33.834390)->(-85.585332,33.838537)',1,'');
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=MyISAM AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission'),(2,'group','auth','group'),(3,'user','auth','user'),(4,'message','auth','message'),(5,'content type','contenttypes','contenttype'),(6,'session','sessions','session'),(7,'site','sites','site'),(8,'log entry','admin','logentry'),(9,'rating type','ratestreets','ratingtype'),(10,'category','ratestreets','category'),(11,'item','ratestreets','item'),(12,'module','ratestreets','module'),(13,'project','ratestreets','project'),(14,'study','ratestreets','study'),(15,'segment','ratestreets','segment'),(16,'step','ratestreets','step'),(17,'boolean rating','ratestreets','booleanrating'),(18,'category rating','ratestreets','categoryrating'),(19,'count rating','ratestreets','countrating'),(20,'free form rating','ratestreets','freeformrating'),(21,'rating task','ratestreets','ratingtask');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('808ff1860153ecda0d2f24f2768b9273','gAJ9cQEoVRJfYXV0aF91c2VyX2JhY2tlbmRxAlUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxA1UNX2F1dGhfdXNlcl9pZHEEigEBdS41YjU2ZWQ2ZDMyMmRlNTU3Yzlj\nYmI1NDJmZWZmMjk3Nw==\n','2011-02-02 16:51:57');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_booleanrating`
--

DROP TABLE IF EXISTS `ratestreets_booleanrating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_booleanrating` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `rating` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratestreets_booleanrating_fbfc09f1` (`user_id`),
  KEY `ratestreets_booleanrating_67b70d25` (`item_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_booleanrating`
--

LOCK TABLES `ratestreets_booleanrating` WRITE;
/*!40000 ALTER TABLE `ratestreets_booleanrating` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratestreets_booleanrating` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_category`
--

DROP TABLE IF EXISTS `ratestreets_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `description` varchar(256) NOT NULL,
  `value` int(10) unsigned NOT NULL,
  `category_group_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratestreets_category_69b1aa12` (`category_group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_category`
--

LOCK TABLES `ratestreets_category` WRITE;
/*!40000 ALTER TABLE `ratestreets_category` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratestreets_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_categoryrating`
--

DROP TABLE IF EXISTS `ratestreets_categoryrating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_categoryrating` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `rating` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratestreets_categoryrating_fbfc09f1` (`user_id`),
  KEY `ratestreets_categoryrating_67b70d25` (`item_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_categoryrating`
--

LOCK TABLES `ratestreets_categoryrating` WRITE;
/*!40000 ALTER TABLE `ratestreets_categoryrating` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratestreets_categoryrating` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_categoryratingtype`
--

DROP TABLE IF EXISTS `ratestreets_categoryratingtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_categoryratingtype` (
  `ratingtype_ptr_id` int(11) NOT NULL,
  `category_name` varchar(32) NOT NULL,
  PRIMARY KEY (`ratingtype_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_categoryratingtype`
--

LOCK TABLES `ratestreets_categoryratingtype` WRITE;
/*!40000 ALTER TABLE `ratestreets_categoryratingtype` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratestreets_categoryratingtype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_countrating`
--

DROP TABLE IF EXISTS `ratestreets_countrating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_countrating` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `rating` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratestreets_countrating_fbfc09f1` (`user_id`),
  KEY `ratestreets_countrating_67b70d25` (`item_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_countrating`
--

LOCK TABLES `ratestreets_countrating` WRITE;
/*!40000 ALTER TABLE `ratestreets_countrating` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratestreets_countrating` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_freeformrating`
--

DROP TABLE IF EXISTS `ratestreets_freeformrating`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_freeformrating` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `rating` varchar(1024) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratestreets_freeformrating_fbfc09f1` (`user_id`),
  KEY `ratestreets_freeformrating_67b70d25` (`item_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_freeformrating`
--

LOCK TABLES `ratestreets_freeformrating` WRITE;
/*!40000 ALTER TABLE `ratestreets_freeformrating` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratestreets_freeformrating` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_item`
--

DROP TABLE IF EXISTS `ratestreets_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `description` varchar(256) NOT NULL,
  `source` varchar(32) NOT NULL,
  `rating_type_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratestreets_item_25508c81` (`rating_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_item`
--

LOCK TABLES `ratestreets_item` WRITE;
/*!40000 ALTER TABLE `ratestreets_item` DISABLE KEYS */;
INSERT INTO `ratestreets_item` VALUES (1,'Paved','Is the street paved?','Bogus',1,'2011-01-20 11:38:07','2011-01-20 11:38:07');
/*!40000 ALTER TABLE `ratestreets_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_module`
--

DROP TABLE IF EXISTS `ratestreets_module`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_module` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(256) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_module`
--

LOCK TABLES `ratestreets_module` WRITE;
/*!40000 ALTER TABLE `ratestreets_module` DISABLE KEYS */;
INSERT INTO `ratestreets_module` VALUES (1,'Test Module','2011-01-20 11:38:22','2011-01-20 11:38:22');
/*!40000 ALTER TABLE `ratestreets_module` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_module_items`
--

DROP TABLE IF EXISTS `ratestreets_module_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_module_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `module_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `module_id` (`module_id`,`item_id`),
  KEY `item_id_refs_id_7bc86283` (`item_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_module_items`
--

LOCK TABLES `ratestreets_module_items` WRITE;
/*!40000 ALTER TABLE `ratestreets_module_items` DISABLE KEYS */;
INSERT INTO `ratestreets_module_items` VALUES (1,1,1);
/*!40000 ALTER TABLE `ratestreets_module_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_project`
--

DROP TABLE IF EXISTS `ratestreets_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_project` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `director_id` int(11) NOT NULL,
  `name` varchar(32) NOT NULL,
  `description` varchar(256) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratestreets_project_81c0b88c` (`director_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_project`
--

LOCK TABLES `ratestreets_project` WRITE;
/*!40000 ALTER TABLE `ratestreets_project` DISABLE KEYS */;
INSERT INTO `ratestreets_project` VALUES (1,1,'Simple Test Project','Simple Test Project','2011-01-20 11:38:49','2011-01-20 11:38:49');
/*!40000 ALTER TABLE `ratestreets_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_project_managers`
--

DROP TABLE IF EXISTS `ratestreets_project_managers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_project_managers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_id` (`project_id`,`user_id`),
  KEY `user_id_refs_id_a77c3c9d` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_project_managers`
--

LOCK TABLES `ratestreets_project_managers` WRITE;
/*!40000 ALTER TABLE `ratestreets_project_managers` DISABLE KEYS */;
INSERT INTO `ratestreets_project_managers` VALUES (1,1,1);
/*!40000 ALTER TABLE `ratestreets_project_managers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_project_raters`
--

DROP TABLE IF EXISTS `ratestreets_project_raters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_project_raters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_id` (`project_id`,`user_id`),
  KEY `user_id_refs_id_cf84704e` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_project_raters`
--

LOCK TABLES `ratestreets_project_raters` WRITE;
/*!40000 ALTER TABLE `ratestreets_project_raters` DISABLE KEYS */;
INSERT INTO `ratestreets_project_raters` VALUES (1,1,2);
/*!40000 ALTER TABLE `ratestreets_project_raters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_ratingtask`
--

DROP TABLE IF EXISTS `ratestreets_ratingtask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_ratingtask` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `location_content_type_id` int(11) NOT NULL,
  `location_object_id` int(10) unsigned NOT NULL,
  `item_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `first_prompted_at` datetime NOT NULL,
  `completed_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratestreets_ratingtask_fbfc09f1` (`user_id`),
  KEY `ratestreets_ratingtask_65699acf` (`location_content_type_id`),
  KEY `ratestreets_ratingtask_67b70d25` (`item_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_ratingtask`
--

LOCK TABLES `ratestreets_ratingtask` WRITE;
/*!40000 ALTER TABLE `ratestreets_ratingtask` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratestreets_ratingtask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_ratingtype`
--

DROP TABLE IF EXISTS `ratestreets_ratingtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_ratingtype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `storage_type` varchar(32) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_ratingtype`
--

LOCK TABLES `ratestreets_ratingtype` WRITE;
/*!40000 ALTER TABLE `ratestreets_ratingtype` DISABLE KEYS */;
INSERT INTO `ratestreets_ratingtype` VALUES (1,'boolean rating type','BOOL','2011-01-20 11:37:46','2011-01-20 11:37:46');
/*!40000 ALTER TABLE `ratestreets_ratingtype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_segment`
--

DROP TABLE IF EXISTS `ratestreets_segment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_segment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(256) NOT NULL,
  `study_id` int(11) NOT NULL,
  `point_of_view` double NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `start_lat` double NOT NULL,
  `start_lng` double NOT NULL,
  `end_lat` double NOT NULL,
  `end_lng` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratestreets_segment_da5fc7d6` (`study_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_segment`
--

LOCK TABLES `ratestreets_segment` WRITE;
/*!40000 ALTER TABLE `ratestreets_segment` DISABLE KEYS */;
INSERT INTO `ratestreets_segment` VALUES (1,'Simple Test Segment',1,0,'2011-01-20 11:39:49','2011-01-20 11:39:49',-85.585406,33.83439,-85.585332,33.838537);
/*!40000 ALTER TABLE `ratestreets_segment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_step`
--

DROP TABLE IF EXISTS `ratestreets_step`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_step` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(256) NOT NULL,
  `study_id` int(11) NOT NULL,
  `point_of_view` double NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `lat` double NOT NULL,
  `lng` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratestreets_step_da5fc7d6` (`study_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_step`
--

LOCK TABLES `ratestreets_step` WRITE;
/*!40000 ALTER TABLE `ratestreets_step` DISABLE KEYS */;
/*!40000 ALTER TABLE `ratestreets_step` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_study`
--

DROP TABLE IF EXISTS `ratestreets_study`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_study` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(256) NOT NULL,
  `project_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ratestreets_study_b6620684` (`project_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_study`
--

LOCK TABLES `ratestreets_study` WRITE;
/*!40000 ALTER TABLE `ratestreets_study` DISABLE KEYS */;
INSERT INTO `ratestreets_study` VALUES (1,'Simple Test Study',1,'2011-01-20 11:39:12','2011-01-20 11:39:12');
/*!40000 ALTER TABLE `ratestreets_study` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ratestreets_study_modules`
--

DROP TABLE IF EXISTS `ratestreets_study_modules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ratestreets_study_modules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `study_id` int(11) NOT NULL,
  `module_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `study_id` (`study_id`,`module_id`),
  KEY `module_id_refs_id_77b4b54f` (`module_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ratestreets_study_modules`
--

LOCK TABLES `ratestreets_study_modules` WRITE;
/*!40000 ALTER TABLE `ratestreets_study_modules` DISABLE KEYS */;
INSERT INTO `ratestreets_study_modules` VALUES (1,1,1);
/*!40000 ALTER TABLE `ratestreets_study_modules` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2011-01-20 12:40:15
