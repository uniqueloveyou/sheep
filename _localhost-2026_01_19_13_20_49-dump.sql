-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: sheep_db
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add 羊只信息',9,'add_sheep'),(26,'Can change 羊只信息',9,'change_sheep'),(27,'Can delete 羊只信息',9,'delete_sheep'),(28,'Can view 羊只信息',9,'view_sheep'),(29,'Can add 喂养记录',10,'add_feedingrecord'),(30,'Can change 喂养记录',10,'change_feedingrecord'),(31,'Can delete 喂养记录',10,'delete_feedingrecord'),(32,'Can view 喂养记录',10,'view_feedingrecord'),(33,'Can add 购物车商品',11,'add_cartitem'),(34,'Can change 购物车商品',11,'change_cartitem'),(35,'Can delete 购物车商品',11,'delete_cartitem'),(36,'Can view 购物车商品',11,'view_cartitem'),(37,'Can add 养殖户信息',8,'add_breeder'),(38,'Can change 养殖户信息',8,'change_breeder'),(39,'Can delete 养殖户信息',8,'delete_breeder'),(40,'Can view 养殖户信息',8,'view_breeder'),(41,'Can add 用户',7,'add_user'),(42,'Can change 用户',7,'change_user'),(43,'Can delete 用户',7,'delete_user'),(44,'Can view 用户',7,'view_user'),(45,'Can add 生长记录',12,'add_growthrecord'),(46,'Can change 生长记录',12,'change_growthrecord'),(47,'Can delete 生长记录',12,'delete_growthrecord'),(48,'Can view 生长记录',12,'view_growthrecord'),(49,'Can add 疫苗接种记录',13,'add_vaccinationhistory'),(50,'Can change 疫苗接种记录',13,'change_vaccinationhistory'),(51,'Can delete 疫苗接种记录',13,'delete_vaccinationhistory'),(52,'Can view 疫苗接种记录',13,'view_vaccinationhistory');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES (1,'pbkdf2_sha256$1000000$VshxY37wI47NU4QkAed3ys$NRPaMbP/CLaD4ZENWkab9cW3iWDDZscx7U7Lucy7Wfo=','2025-12-23 07:43:47.528481',1,'admin','','','123@123.com',1,1,'2025-12-04 08:47:33.063566');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `breeders`
--

DROP TABLE IF EXISTS `breeders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `breeders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '姓名',
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '性别（男/女）',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '联系电话',
  `sheep_count` int NOT NULL COMMENT '羊只总数',
  `sheep_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '羊只编号',
  `female_count` int NOT NULL COMMENT '母羊数量',
  `male_count` int NOT NULL COMMENT '公羊数量',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_sheep_id` (`sheep_id`) USING BTREE,
  KEY `idx_name` (`name`) USING BTREE,
  KEY `idx_phone` (`phone`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='养殖户信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `breeders`
--

LOCK TABLES `breeders` WRITE;
/*!40000 ALTER TABLE `breeders` DISABLE KEYS */;
INSERT INTO `breeders` (`id`, `name`, `gender`, `phone`, `sheep_count`, `sheep_id`, `female_count`, `male_count`) VALUES (1,'张三','男','13800138000',100,'X12345678',50,50),(2,'李四','女','13900139000',80,'X23456789',45,35),(3,'王五','男','13700137000',120,'X34567890',60,60),(4,'李强','男','13812340001',120,'Y20250001',70,50),(5,'王芳','女','13912340002',85,'Y20250002',50,35),(6,'张伟','男','13712340003',60,'Y20250003',40,20),(7,'刘洋','女','15012340004',95,'Y20250004',60,35),(8,'陈静','女','18612340005',110,'Y20250005',65,45),(9,'杨勇','男','15812340006',75,'Y20250006',45,30),(10,'赵敏','女','13612340007',50,'Y20250007',30,20),(11,'黄磊','男','13512340008',130,'Y20250008',80,50),(12,'周杰','男','13412340009',90,'Y20250009',55,35),(13,'吴艳','女','18912340010',65,'Y20250010',40,25),(14,'徐涛','男','17712340011',105,'Y20250011',60,45),(15,'孙丽','女','15912340012',70,'Y20250012',45,25),(16,'胡军','男','15112340013',115,'Y20250013',70,45),(17,'朱红','女','15212340014',80,'Y20250014',50,30),(18,'高飞','男','13312340015',125,'Y20250015',75,50),(19,'林娜','女','15312340016',55,'Y20250016',35,20),(20,'何伟','男','18812340017',140,'Y20250017',85,55),(21,'郭平','男','18712340018',95,'Y20250018',60,35),(22,'马兰','女','13012340019',45,'Y20250019',25,20),(23,'罗强','男','13112340020',100,'Y20250020',60,40),(24,'梁斌','男','13212340021',88,'Y20250021',50,38),(25,'宋梅','女','15512340022',72,'Y20250022',42,30),(26,'郑华','男','15612340023',112,'Y20250023',68,44),(27,'谢婷','女','18512340024',66,'Y20250024',40,26),(28,'韩冰','男','18012340025',135,'Y20250025',80,55),(29,'唐杰','男','18112340026',92,'Y20250026',55,37),(30,'冯雪','女','13812340027',58,'Y20250027',35,23),(31,'于成','男','13912340028',108,'Y20250028',65,43),(32,'董霞','女','13712340029',78,'Y20250029',48,30),(33,'萧峰','男','15012340030',122,'Y20250030',75,47),(34,'程刚','男','18612340031',86,'Y20250031',52,34),(35,'曹云','女','15812340032',62,'Y20250032',38,24),(36,'袁波','男','13612340033',118,'Y20250033',72,46),(37,'邓超','男','13512340034',96,'Y20250034',58,38),(38,'许倩','女','13412340035',74,'Y20250035',44,30),(39,'傅强','男','18912340036',128,'Y20250036',78,50),(40,'沈洁','女','17712340037',82,'Y20250037',50,32),(41,'曾勇','男','15912340038',56,'Y20250038',34,22),(42,'彭丽','女','15112340039',102,'Y20250039',62,40),(43,'吕刚','男','15212340040',84,'Y20250040',50,34),(44,'苏华','男','13312340041',68,'Y20250041',40,28),(45,'卢伟','男','15312340042',114,'Y20250042',68,46),(46,'蒋敏','女','18812340043',94,'Y20250043',56,38),(47,'蔡军','男','18712340044',76,'Y20250044',46,30),(48,'贾玲','女','13012340045',126,'Y20250045',76,50),(49,'丁明','男','13112340046',88,'Y20250046',54,34),(50,'魏芳','女','13212340047',64,'Y20250047',38,26),(51,'薛松','男','15512340048',106,'Y20250048',64,42),(52,'叶琳','女','15612340049',82,'Y20250049',48,34),(53,'阎罗','男','18512340050',52,'Y20250050',32,20),(54,'余海','男','18012340051',132,'Y20250051',80,52),(55,'潘越','男','18112340052',98,'Y20250052',58,40),(56,'杜鹃','女','13812340053',70,'Y20250053',42,28),(57,'戴维','男','13912340054',116,'Y20250054',70,46),(58,'夏荷','女','13712340055',84,'Y20250055',52,32),(59,'钟强','男','15012340056',60,'Y20250056',36,24),(60,'汪洋','男','18612340057',104,'Y20250057',62,42),(61,'田雨','女','15812340058',86,'Y20250058',52,34),(62,'任重','男','13612340059',54,'Y20250059',34,20),(63,'姜文','男','13512340060',124,'Y20250060',74,50),(64,'范冰','女','13412340061',92,'Y20250061',56,36),(65,'方正','男','18912340062',74,'Y20250062',44,30),(66,'石磊','男','17712340063',112,'Y20250063',68,44),(67,'姚琴','女','15912340064',88,'Y20250064',54,34),(68,'谭虎','男','15112340065',66,'Y20250065',40,26),(69,'廖凡','男','15212340066',108,'Y20250066',64,44),(70,'邹忌','男','13312340067',80,'Y20250067',48,32),(71,'熊大','男','15312340068',58,'Y20250068',36,22),(72,'孟母','女','18812340069',120,'Y20250069',72,48),(73,'秦岭','男','18712340070',94,'Y20250070',58,36),(74,'白云','女','13012340071',72,'Y20250071',42,30),(75,'江水','男','13112340072',110,'Y20250072',66,44),(76,'钱多多','男','13212340073',85,'Y20250073',50,35),(77,'邵逸','男','15512340074',62,'Y20250074',38,24),(78,'尹红','女','15612340075',102,'Y20250075',60,42),(79,'孔明','男','18512340076',78,'Y20250076',46,32),(80,'崔健','男','18012340077',55,'Y20250077',35,20),(81,'康熙','男','18112340078',130,'Y20250078',78,52),(82,'毛毛','女','13812340079',90,'Y20250079',54,36),(83,'邱少','男','13912340080',68,'Y20250080',40,28),(84,'贺礼','男','13712340081',114,'Y20250081',68,46),(85,'龚琳','女','15012340082',84,'Y20250082',50,34),(86,'文强','男','18612340083',58,'Y20250083',34,24),(87,'庞统','男','15812340084',106,'Y20250084',62,44),(88,'常乐','女','13612340085',76,'Y20250085',46,30),(89,'牛群','男','13512340086',52,'Y20250086',32,20),(90,'耿直','男','13412340087',125,'Y20250087',75,50),(91,'莫言','男','18912340088',96,'Y20250088',58,38),(92,'焦大','男','17712340089',74,'Y20250089',44,30),(93,'向往','女','15912340090',118,'Y20250090',70,48),(94,'邢台','男','15112340091',82,'Y20250091',50,32),(95,'易中','男','15212340092',60,'Y20250092',36,24),(96,'乔峰','男','13312340093',108,'Y20250093',64,44),(97,'伍月','女','15312340094',86,'Y20250094',52,34),(98,'齐天','男','18812340095',56,'Y20250095',34,22),(99,'庄周','男','18712340096',116,'Y20250096',70,46),(100,'樊胜','女','13012340097',92,'Y20250097',56,36),(101,'颜回','男','13112340098',72,'Y20250098',42,30),(102,'梅超','女','13212340099',104,'Y20250099',62,42),(103,'骆驼','男','15512340100',80,'Y20250100',48,32);
/*!40000 ALTER TABLE `breeders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '用户ID',
  `sheep_id` int NOT NULL COMMENT '羊只ID',
  `quantity` int NOT NULL DEFAULT '1' COMMENT '数量',
  `price` float NOT NULL COMMENT '单价',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '添加时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_sheep` (`user_id`,`sheep_id`) USING BTREE COMMENT '同一用户同一羊只只能有一条记录',
  KEY `idx_user_id` (`user_id`) USING BTREE,
  KEY `idx_sheep_id` (`sheep_id`) USING BTREE,
  KEY `idx_created_at` (`created_at`) USING BTREE,
  CONSTRAINT `cart_items_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `cart_items_ibfk_2` FOREIGN KEY (`sheep_id`) REFERENCES `sheep` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='购物车表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
INSERT INTO `cart_items` (`id`, `user_id`, `sheep_id`, `quantity`, `price`, `created_at`, `updated_at`) VALUES (1,1,1,1,455,'2025-12-04 10:03:18','2025-12-04 10:03:18'),(2,1,2,1,100,'2025-12-23 07:45:39','2025-12-23 07:45:39'),(3,1,4,1,100,'2025-12-23 07:46:09','2025-12-23 07:46:09');
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `coupons`
--

DROP TABLE IF EXISTS `coupons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `coupons` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '优惠券名称',
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '优惠券代码',
  `coupon_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '优惠券类型：discount(满减券), percentage(折扣券), cash(现金券)',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active' COMMENT '状态：active(可用), inactive(不可用), expired(已过期)',
  `discount_amount` float DEFAULT NULL COMMENT '优惠金额（满减券/现金券）',
  `discount_rate` float DEFAULT NULL COMMENT '折扣率（折扣券，0-1）',
  `min_purchase_amount` float NOT NULL DEFAULT '0' COMMENT '最低消费金额',
  `max_discount_amount` float DEFAULT NULL COMMENT '最大折扣金额',
  `total_count` int DEFAULT NULL COMMENT '总发放数量',
  `used_count` int NOT NULL DEFAULT '0' COMMENT '已使用数量',
  `user_limit` int NOT NULL DEFAULT '1' COMMENT '每用户限领数量',
  `valid_from` datetime NOT NULL COMMENT '生效时间',
  `valid_until` datetime NOT NULL COMMENT '失效时间',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '使用说明',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_code` (`code`) USING BTREE,
  KEY `idx_status` (`status`) USING BTREE,
  KEY `idx_coupon_type` (`coupon_type`) USING BTREE,
  KEY `idx_valid_from` (`valid_from`) USING BTREE,
  KEY `idx_valid_until` (`valid_until`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='优惠券表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `coupons`
--

LOCK TABLES `coupons` WRITE;
/*!40000 ALTER TABLE `coupons` DISABLE KEYS */;
INSERT INTO `coupons` (`id`, `name`, `code`, `coupon_type`, `status`, `discount_amount`, `discount_rate`, `min_purchase_amount`, `max_discount_amount`, `total_count`, `used_count`, `user_limit`, `valid_from`, `valid_until`, `description`, `created_at`, `updated_at`) VALUES (1,'新人见面礼','NEW2026','cash','active',50,NULL,0,NULL,10000,120,1,'2025-01-01 00:00:00','2026-12-31 23:59:59','新用户注册即可领取，无门槛立减50元','2025-12-06 15:32:43','2025-12-06 15:32:43'),(2,'满2000减200','OFF200','discount','active',200,NULL,2000,NULL,500,30,2,'2025-11-01 00:00:00','2026-03-31 23:59:59','购买整羊或大额订单适用','2025-12-06 15:32:43','2025-12-06 15:32:43'),(3,'全场95折','DISC95','percentage','active',NULL,0.95,0,NULL,2000,450,5,'2025-01-01 00:00:00','2026-12-31 23:59:59','不限金额，全场通用95折','2025-12-06 15:32:43','2025-12-06 15:32:43'),(4,'过期优惠券测试','EXPIRED','cash','expired',20,NULL,0,NULL,100,100,1,'2024-01-01 00:00:00','2024-12-31 23:59:59','这是一张已过期的券','2025-12-06 15:32:43','2025-12-06 15:32:43');
/*!40000 ALTER TABLE `coupons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES (1,'2025-12-04 08:58:57.825642','1','1',1,'[{\"added\": {}}]',7,1),(2,'2025-12-23 07:45:39.502252','2','测试用户 - 羊只#2 - 雌性 - 42.3kg - 1件',1,'[{\"added\": {}}]',11,1),(3,'2025-12-23 07:46:04.706470','4','羊只#4 - 母 - 55.0kg',1,'[{\"added\": {}}]',9,1),(4,'2025-12-23 07:46:09.162176','3','测试用户 - 羊只#4 - 母 - 55.0kg - 1件',1,'[{\"added\": {}}]',11,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(6,'sessions','session'),(8,'sheep_management','breeder'),(11,'sheep_management','cartitem'),(10,'sheep_management','feedingrecord'),(12,'sheep_management','growthrecord'),(9,'sheep_management','sheep'),(7,'sheep_management','user'),(13,'sheep_management','vaccinationhistory');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES (1,'contenttypes','0001_initial','2025-12-04 08:46:28.097212'),(2,'auth','0001_initial','2025-12-04 08:46:29.093183'),(3,'admin','0001_initial','2025-12-04 08:46:29.267155'),(4,'admin','0002_logentry_remove_auto_add','2025-12-04 08:46:29.285341'),(5,'admin','0003_logentry_add_action_flag_choices','2025-12-04 08:46:29.292833'),(6,'contenttypes','0002_remove_content_type_name','2025-12-04 08:46:29.429487'),(7,'auth','0002_alter_permission_name_max_length','2025-12-04 08:46:29.524860'),(8,'auth','0003_alter_user_email_max_length','2025-12-04 08:46:29.548898'),(9,'auth','0004_alter_user_username_opts','2025-12-04 08:46:29.557794'),(10,'auth','0005_alter_user_last_login_null','2025-12-04 08:46:29.626221'),(11,'auth','0006_require_contenttypes_0002','2025-12-04 08:46:29.630152'),(12,'auth','0007_alter_validators_add_error_messages','2025-12-04 08:46:29.639213'),(13,'auth','0008_alter_user_username_max_length','2025-12-04 08:46:29.726047'),(14,'auth','0009_alter_user_last_name_max_length','2025-12-04 08:46:29.812849'),(15,'auth','0010_alter_group_name_max_length','2025-12-04 08:46:29.842727'),(16,'auth','0011_update_proxy_permissions','2025-12-04 08:46:29.851671'),(17,'auth','0012_alter_user_first_name_max_length','2025-12-04 08:46:29.945851'),(18,'sessions','0001_initial','2025-12-04 08:46:29.999309'),(19,'sheep_management','0001_initial','2025-12-04 13:08:31.156055');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES ('bsdtn6k4alicqcd70s9q8ys1uo83zy3h','.eJxVjEEOwiAQRe_C2hCYUqAu3XsGwjCDVA0kpV0Z765NutDtf-_9lwhxW0vYOi9hJnEWWpx-N4zpwXUHdI_11mRqdV1mlLsiD9rltRE_L4f7d1BiL98aEKI3nC2NxOS8UoTeTzqBVsqSmgjBWTRkeByG6CE7p4gZNFqbwYv3B-gZN9A:1vR5AY:1Vadz0uZ1lTKOcRly9ANOM6OZWoa3ls4chdz5VnRcFo','2025-12-18 08:58:34.471569'),('s4k80cwgwrrkr3th8mq4af1nwt4yrnjq','.eJxVjEEOwiAQRe_C2hCYUqAu3XsGwjCDVA0kpV0Z765NutDtf-_9lwhxW0vYOi9hJnEWWpx-N4zpwXUHdI_11mRqdV1mlLsiD9rltRE_L4f7d1BiL98aEKI3nC2NxOS8UoTeTzqBVsqSmgjBWTRkeByG6CE7p4gZNFqbwYv3B-gZN9A:1vR7xD:Po83LNczATgphDippXsIqufngVnma9o2hGJfXwAzOqc','2025-12-18 11:56:59.433744'),('zu9xvvykfe30wuz07th4bblyvuqsw249','.eJxVjEEOwiAQRe_C2hCYUqAu3XsGwjCDVA0kpV0Z765NutDtf-_9lwhxW0vYOi9hJnEWWpx-N4zpwXUHdI_11mRqdV1mlLsiD9rltRE_L4f7d1BiL98aEKI3nC2NxOS8UoTeTzqBVsqSmgjBWTRkeByG6CE7p4gZNFqbwYv3B-gZN9A:1vXx3b:gPI_ZYm3obyAtVZ50Jljz8_bcE7lJIWHAhPXhZZbgGA','2026-01-06 07:43:47.556515');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feeding_records`
--

DROP TABLE IF EXISTS `feeding_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feeding_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sheep_id` int NOT NULL COMMENT '羊只ID',
  `feed_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '饲料类型',
  `start_date` date NOT NULL COMMENT '开始日期',
  `end_date` date DEFAULT NULL COMMENT '结束日期',
  `amount` float NOT NULL COMMENT '数量',
  `unit` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '单位',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_sheep_id` (`sheep_id`) USING BTREE,
  KEY `idx_start_date` (`start_date`) USING BTREE,
  CONSTRAINT `feeding_records_ibfk_1` FOREIGN KEY (`sheep_id`) REFERENCES `sheep` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='喂养记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feeding_records`
--

LOCK TABLES `feeding_records` WRITE;
/*!40000 ALTER TABLE `feeding_records` DISABLE KEYS */;
INSERT INTO `feeding_records` (`id`, `sheep_id`, `feed_type`, `start_date`, `end_date`, `amount`, `unit`) VALUES (1,1,'青草','2024-01-01','2024-01-31',30,'kg'),(2,1,'精饲料','2024-02-01',NULL,5,'kg'),(3,2,'青草','2024-01-01','2024-01-31',28,'kg');
/*!40000 ALTER TABLE `feeding_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `growth_records`
--

DROP TABLE IF EXISTS `growth_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `growth_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sheep_id` int NOT NULL COMMENT '羊只ID',
  `record_date` date NOT NULL COMMENT '记录日期',
  `weight` float NOT NULL COMMENT '体重（kg）',
  `height` float NOT NULL COMMENT '身高（cm）',
  `length` float NOT NULL COMMENT '体长（cm）',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_sheep_date` (`sheep_id`,`record_date`),
  KEY `idx_sheep_id` (`sheep_id`) USING BTREE,
  KEY `idx_record_date` (`record_date`) USING BTREE,
  CONSTRAINT `growth_records_ibfk_1` FOREIGN KEY (`sheep_id`) REFERENCES `sheep` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='生长记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `growth_records`
--

LOCK TABLES `growth_records` WRITE;
/*!40000 ALTER TABLE `growth_records` DISABLE KEYS */;
INSERT INTO `growth_records` (`id`, `sheep_id`, `record_date`, `weight`, `height`, `length`) VALUES (1,1,'2024-01-01',40,60,85),(2,1,'2024-02-01',42.5,62,88),(3,2,'2024-01-01',38,58,82),(4,1,'2026-01-01',70,80,100);
/*!40000 ALTER TABLE `growth_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `promotion_activities`
--

DROP TABLE IF EXISTS `promotion_activities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `promotion_activities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '活动标题',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '活动描述',
  `activity_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '活动类型：flash_sale(限时抢购), package(套餐活动), discount(折扣活动)',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft' COMMENT '状态：draft(草稿), active(进行中), ended(已结束), cancelled(已取消)',
  `image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '活动图片',
  `start_time` datetime NOT NULL COMMENT '开始时间',
  `end_time` datetime NOT NULL COMMENT '结束时间',
  `discount_rate` float DEFAULT NULL COMMENT '折扣率（0-1）',
  `discount_amount` float DEFAULT NULL COMMENT '折扣金额',
  `min_purchase_amount` float DEFAULT '0' COMMENT '最低消费金额',
  `max_discount_amount` float DEFAULT NULL COMMENT '最大折扣金额',
  `total_limit` int DEFAULT NULL COMMENT '总限购数量',
  `user_limit` int DEFAULT '1' COMMENT '每用户限购数量',
  `sold_count` int NOT NULL DEFAULT '0' COMMENT '已售数量',
  `applicable_sheep_ids` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '适用羊只ID列表（JSON格式）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_status` (`status`) USING BTREE,
  KEY `idx_activity_type` (`activity_type`) USING BTREE,
  KEY `idx_start_time` (`start_time`) USING BTREE,
  KEY `idx_end_time` (`end_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='优惠活动表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `promotion_activities`
--

LOCK TABLES `promotion_activities` WRITE;
/*!40000 ALTER TABLE `promotion_activities` DISABLE KEYS */;
INSERT INTO `promotion_activities` (`id`, `title`, `description`, `activity_type`, `status`, `image_url`, `start_time`, `end_time`, `discount_rate`, `discount_amount`, `min_purchase_amount`, `max_discount_amount`, `total_limit`, `user_limit`, `sold_count`, `applicable_sheep_ids`, `created_at`, `updated_at`) VALUES (1,'2025暖冬特惠套餐','冬季进补首选，包含3只精选滩羊，赠送专用调料包。','package','active','/images/winter_sale.jpg','2025-11-01 00:00:00','2026-02-28 23:59:59',0.85,NULL,0,NULL,50,1,12,'[1, 3]','2025-12-06 15:32:43','2025-12-06 15:32:43'),(2,'跨年限时秒杀','跨年夜当晚开启，全场6折起，手慢无！','flash_sale','active','/images/new_year.jpg','2025-12-01 00:00:00','2026-01-05 23:59:59',0.6,NULL,0,NULL,100,1,45,NULL,'2025-12-06 15:32:43','2025-12-06 15:32:43'),(3,'新春预热满减','迎接2026农历新年，全场满1000减150。','discount','active','/images/spring_fest.jpg','2025-12-15 00:00:00','2026-02-15 23:59:59',NULL,NULL,1000,NULL,500,2,8,NULL,'2025-12-06 15:32:43','2025-12-06 15:32:43'),(4,'往期活动-秋季大促','已结束的活动测试数据。','discount','ended','/images/autumn.jpg','2025-09-01 00:00:00','2025-10-31 23:59:59',0.9,NULL,0,NULL,200,5,180,NULL,'2025-12-06 15:32:43','2025-12-06 15:32:43');
/*!40000 ALTER TABLE `promotion_activities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sheep`
--

DROP TABLE IF EXISTS `sheep`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sheep` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '性别（公/母）',
  `weight` float NOT NULL COMMENT '体重（kg）',
  `height` float NOT NULL COMMENT '身高（cm）',
  `length` float NOT NULL COMMENT '体长（cm）',
  `breeder_id` int DEFAULT NULL COMMENT '养殖户ID',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='羊只基本信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sheep`
--

LOCK TABLES `sheep` WRITE;
/*!40000 ALTER TABLE `sheep` DISABLE KEYS */;
INSERT INTO `sheep` (`id`, `gender`, `weight`, `height`, `length`, `breeder_id`) VALUES (1,'雄性',45.5,65,95,1),(2,'雌性',42.3,62,90,2),(3,'雄性',48.2,68,98,3),(4,'母',55,66,77,9);
/*!40000 ALTER TABLE `sheep` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_coupons`
--

DROP TABLE IF EXISTS `user_coupons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_coupons` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '用户ID',
  `coupon_id` int NOT NULL COMMENT '优惠券ID',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'unused' COMMENT '使用状态：unused(未使用), used(已使用), expired(已过期)',
  `obtained_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '领取时间',
  `used_at` datetime DEFAULT NULL COMMENT '使用时间',
  `order_id` int DEFAULT NULL COMMENT '使用的订单ID',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_user_coupon` (`user_id`,`coupon_id`) USING BTREE COMMENT '同一用户同一优惠券只能有一条记录',
  KEY `idx_user_status` (`user_id`,`status`) USING BTREE,
  KEY `idx_coupon_status` (`coupon_id`,`status`) USING BTREE,
  KEY `idx_obtained_at` (`obtained_at`) USING BTREE,
  CONSTRAINT `user_coupons_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `user_coupons_ibfk_2` FOREIGN KEY (`coupon_id`) REFERENCES `coupons` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='用户优惠券关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_coupons`
--

LOCK TABLES `user_coupons` WRITE;
/*!40000 ALTER TABLE `user_coupons` DISABLE KEYS */;
INSERT INTO `user_coupons` (`id`, `user_id`, `coupon_id`, `status`, `obtained_at`, `used_at`, `order_id`) VALUES (1,1,1,'unused','2025-12-06 15:32:43',NULL,NULL),(2,1,2,'unused','2025-12-06 15:32:43',NULL,NULL),(3,1,3,'used','2025-11-20 10:00:00','2025-11-25 14:00:00',1001),(4,1,4,'expired','2024-10-01 10:00:00',NULL,NULL);
/*!40000 ALTER TABLE `user_coupons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `openid` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '微信openid',
  `unionid` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '微信unionid',
  `username` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `nickname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '昵称',
  `avatar_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像URL',
  `mobile` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '手机号',
  `gender` int DEFAULT NULL COMMENT '性别：0-未知，1-男，2-女',
  `country` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '国家',
  `province` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '省份',
  `city` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '城市',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `last_login_at` datetime DEFAULT NULL COMMENT '最后登录时间',
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_openid` (`openid`) USING BTREE,
  KEY `idx_openid` (`openid`) USING BTREE,
  KEY `idx_unionid` (`unionid`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` (`id`, `openid`, `unionid`, `username`, `nickname`, `avatar_url`, `mobile`, `gender`, `country`, `province`, `city`, `created_at`, `updated_at`, `last_login_at`, `password`) VALUES (1,'test_openid_001',NULL,'test_user','测试用户',NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-06 15:32:43','2025-12-06 15:32:43',NULL,'123456');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vaccinationhistory`
--

DROP TABLE IF EXISTS `vaccinationhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vaccinationhistory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `VaccinationID` int NOT NULL COMMENT '疫苗类型ID（1:口蹄疫苗, 2:传染性胸膜肺炎灭活疫苗, 3:四联苗）',
  `sheep_id` int NOT NULL COMMENT '羊只ID',
  `VaccinationDate` date NOT NULL COMMENT '接种日期',
  `ExpiryDate` date NOT NULL COMMENT '过期日期',
  `Dosage` float NOT NULL COMMENT '剂量（ml）',
  `AdministeredBy` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '接种人',
  `Notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `VaccineType` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '疫苗类型名称',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_sheep_id` (`sheep_id`) USING BTREE,
  KEY `idx_vaccination_date` (`VaccinationDate`) USING BTREE,
  KEY `idx_vaccination_id` (`VaccinationID`) USING BTREE,
  CONSTRAINT `vaccinationhistory_ibfk_1` FOREIGN KEY (`sheep_id`) REFERENCES `sheep` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='疫苗接种历史表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vaccinationhistory`
--

LOCK TABLES `vaccinationhistory` WRITE;
/*!40000 ALTER TABLE `vaccinationhistory` DISABLE KEYS */;
INSERT INTO `vaccinationhistory` (`id`, `VaccinationID`, `sheep_id`, `VaccinationDate`, `ExpiryDate`, `Dosage`, `AdministeredBy`, `Notes`, `VaccineType`) VALUES (1,1,1,'2024-07-20','2025-07-20',1,'张兽医','接种后无不良反应','口蹄疫苗'),(2,2,1,'2024-07-20','2025-07-20',3,'张兽医','接种后无不良反应','传染性胸膜肺炎灭活疫苗'),(3,1,2,'2024-07-20','2025-07-20',1,'李兽医','接种后无不良反应','口蹄疫苗'),(4,1,3,'2025-11-10','2026-08-08',100,'张量',NULL,'口蹄疫苗');
/*!40000 ALTER TABLE `vaccinationhistory` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-19 13:20:50
