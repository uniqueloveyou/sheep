/*
 Navicat Premium Data Transfer

 Source Server         : 本机
 Source Server Type    : MySQL
 Source Server Version : 80035
 Source Host           : localhost:3306
 Source Schema         : sheep_db

 Target Server Type    : MySQL
 Target Server Version : 80035
 File Encoding         : 65001

 Date: 03/12/2025 10:45:43
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for breeders
-- ----------------------------
DROP TABLE IF EXISTS `breeders`;
CREATE TABLE `breeders`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '姓名',
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '性别（男/女）',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '联系电话',
  `sheep_count` int NOT NULL COMMENT '羊只总数',
  `sheep_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '羊只编号',
  `female_count` int NOT NULL COMMENT '母羊数量',
  `male_count` int NOT NULL COMMENT '公羊数量',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_sheep_id`(`sheep_id` ASC) USING BTREE,
  INDEX `idx_name`(`name` ASC) USING BTREE,
  INDEX `idx_phone`(`phone` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '养殖户信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of breeders
-- ----------------------------
INSERT INTO `breeders` VALUES (1, '张三', '男', '13800138000', 100, 'X12345678', 50, 50);
INSERT INTO `breeders` VALUES (2, '李四', '女', '13900139000', 80, 'X23456789', 45, 35);
INSERT INTO `breeders` VALUES (3, '王五', '男', '13700137000', 120, 'X34567890', 60, 60);

-- ----------------------------
-- Table structure for feeding_records
-- ----------------------------
DROP TABLE IF EXISTS `feeding_records`;
CREATE TABLE `feeding_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `sheep_id` int NOT NULL COMMENT '羊只ID',
  `feed_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '饲料类型',
  `start_date` date NOT NULL COMMENT '开始日期',
  `end_date` date NULL DEFAULT NULL COMMENT '结束日期',
  `amount` float NOT NULL COMMENT '数量',
  `unit` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '单位',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_sheep_id`(`sheep_id` ASC) USING BTREE,
  INDEX `idx_start_date`(`start_date` ASC) USING BTREE,
  CONSTRAINT `feeding_records_ibfk_1` FOREIGN KEY (`sheep_id`) REFERENCES `sheep` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '喂养记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of feeding_records
-- ----------------------------
INSERT INTO `feeding_records` VALUES (1, 1, '青草', '2024-01-01', '2024-01-31', 30, 'kg');
INSERT INTO `feeding_records` VALUES (2, 1, '精饲料', '2024-02-01', NULL, 5, 'kg');
INSERT INTO `feeding_records` VALUES (3, 2, '青草', '2024-01-01', '2024-01-31', 28, 'kg');

-- ----------------------------
-- Table structure for growth_records
-- ----------------------------
DROP TABLE IF EXISTS `growth_records`;
CREATE TABLE `growth_records`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `sheep_id` int NOT NULL COMMENT '羊只ID',
  `record_date` date NOT NULL COMMENT '记录日期',
  `weight` float NOT NULL COMMENT '体重（kg）',
  `height` float NOT NULL COMMENT '身高（cm）',
  `length` float NOT NULL COMMENT '体长（cm）',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_sheep_id`(`sheep_id` ASC) USING BTREE,
  INDEX `idx_record_date`(`record_date` ASC) USING BTREE,
  CONSTRAINT `growth_records_ibfk_1` FOREIGN KEY (`sheep_id`) REFERENCES `sheep` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '生长记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of growth_records
-- ----------------------------
INSERT INTO `growth_records` VALUES (1, 1, '2024-01-01', 40, 60, 85);
INSERT INTO `growth_records` VALUES (2, 1, '2024-02-01', 42.5, 62, 88);
INSERT INTO `growth_records` VALUES (3, 2, '2024-01-01', 38, 58, 82);

-- ----------------------------
-- Table structure for sheep
-- ----------------------------
DROP TABLE IF EXISTS `sheep`;
CREATE TABLE `sheep`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '性别（公/母）',
  `weight` float NOT NULL COMMENT '体重（kg）',
  `height` float NOT NULL COMMENT '身高（cm）',
  `length` float NOT NULL COMMENT '体长（cm）',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '羊只基本信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sheep
-- ----------------------------
INSERT INTO `sheep` VALUES (1, '雄性', 45.5, 65, 95);
INSERT INTO `sheep` VALUES (2, '雌性', 42.3, 62, 90);
INSERT INTO `sheep` VALUES (3, '雄性', 48.2, 68, 98);

-- ----------------------------
-- Table structure for vaccinationhistory
-- ----------------------------
DROP TABLE IF EXISTS `vaccinationhistory`;
CREATE TABLE `vaccinationhistory`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `VaccinationID` int NOT NULL COMMENT '疫苗类型ID（1:口蹄疫苗, 2:传染性胸膜肺炎灭活疫苗, 3:四联苗）',
  `sheep_id` int NOT NULL COMMENT '羊只ID',
  `VaccinationDate` date NOT NULL COMMENT '接种日期',
  `ExpiryDate` date NOT NULL COMMENT '过期日期',
  `Dosage` float NOT NULL COMMENT '剂量（ml）',
  `AdministeredBy` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '接种人',
  `Notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '备注',
  `VaccineType` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '疫苗类型名称',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_sheep_id`(`sheep_id` ASC) USING BTREE,
  INDEX `idx_vaccination_date`(`VaccinationDate` ASC) USING BTREE,
  INDEX `idx_vaccination_id`(`VaccinationID` ASC) USING BTREE,
  CONSTRAINT `vaccinationhistory_ibfk_1` FOREIGN KEY (`sheep_id`) REFERENCES `sheep` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '疫苗接种历史表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of vaccinationhistory
-- ----------------------------
INSERT INTO `vaccinationhistory` VALUES (1, 1, 1, '2024-07-20', '2025-07-20', 1, '张兽医', '接种后无不良反应', '口蹄疫苗');
INSERT INTO `vaccinationhistory` VALUES (2, 2, 1, '2024-07-20', '2025-07-20', 3, '张兽医', '接种后无不良反应', '传染性胸膜肺炎灭活疫苗');
INSERT INTO `vaccinationhistory` VALUES (3, 1, 2, '2024-07-20', '2025-07-20', 1, '李兽医', '接种后无不良反应', '口蹄疫苗');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `openid` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '微信openid',
  `unionid` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '微信unionid',
  `nickname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '昵称',
  `avatar_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '头像URL',
  `mobile` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '手机号',
  `gender` int NULL DEFAULT NULL COMMENT '性别：0-未知，1-男，2-女',
  `country` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '国家',
  `province` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '省份',
  `city` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '城市',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `last_login_at` datetime NULL DEFAULT NULL COMMENT '最后登录时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_openid`(`openid` ASC) USING BTREE,
  INDEX `idx_openid`(`openid` ASC) USING BTREE,
  INDEX `idx_unionid`(`unionid` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户表' ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
