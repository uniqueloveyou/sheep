-- ============================================
-- 优惠活动相关表结构
-- ============================================
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for promotion_activities
-- ----------------------------
DROP TABLE IF EXISTS `promotion_activities`;
CREATE TABLE `promotion_activities`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '活动标题',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '活动描述',
  `activity_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '活动类型：flash_sale(限时抢购), package(套餐活动), discount(折扣活动)',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft' COMMENT '状态：draft(草稿), active(进行中), ended(已结束), cancelled(已取消)',
  `image_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '活动图片',
  `start_time` datetime NOT NULL COMMENT '开始时间',
  `end_time` datetime NOT NULL COMMENT '结束时间',
  `discount_rate` float NULL DEFAULT NULL COMMENT '折扣率（0-1）',
  `discount_amount` float NULL DEFAULT NULL COMMENT '折扣金额',
  `min_purchase_amount` float NULL DEFAULT 0 COMMENT '最低消费金额',
  `max_discount_amount` float NULL DEFAULT NULL COMMENT '最大折扣金额',
  `total_limit` int NULL DEFAULT NULL COMMENT '总限购数量',
  `user_limit` int NULL DEFAULT 1 COMMENT '每用户限购数量',
  `sold_count` int NOT NULL DEFAULT 0 COMMENT '已售数量',
  `applicable_sheep_ids` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '适用羊只ID列表（JSON格式）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE,
  INDEX `idx_activity_type`(`activity_type` ASC) USING BTREE,
  INDEX `idx_start_time`(`start_time` ASC) USING BTREE,
  INDEX `idx_end_time`(`end_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '优惠活动表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for coupons
-- ----------------------------
DROP TABLE IF EXISTS `coupons`;
CREATE TABLE `coupons`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '优惠券名称',
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '优惠券代码',
  `coupon_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '优惠券类型：discount(满减券), percentage(折扣券), cash(现金券)',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active' COMMENT '状态：active(可用), inactive(不可用), expired(已过期)',
  `discount_amount` float NULL DEFAULT NULL COMMENT '优惠金额（满减券/现金券）',
  `discount_rate` float NULL DEFAULT NULL COMMENT '折扣率（折扣券，0-1）',
  `min_purchase_amount` float NOT NULL DEFAULT 0 COMMENT '最低消费金额',
  `max_discount_amount` float NULL DEFAULT NULL COMMENT '最大折扣金额',
  `total_count` int NULL DEFAULT NULL COMMENT '总发放数量',
  `used_count` int NOT NULL DEFAULT 0 COMMENT '已使用数量',
  `user_limit` int NOT NULL DEFAULT 1 COMMENT '每用户限领数量',
  `valid_from` datetime NOT NULL COMMENT '生效时间',
  `valid_until` datetime NOT NULL COMMENT '失效时间',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '使用说明',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_code`(`code` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE,
  INDEX `idx_coupon_type`(`coupon_type` ASC) USING BTREE,
  INDEX `idx_valid_from`(`valid_from` ASC) USING BTREE,
  INDEX `idx_valid_until`(`valid_until` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '优惠券表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_coupons
-- ----------------------------
DROP TABLE IF EXISTS `user_coupons`;
CREATE TABLE `user_coupons`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '用户ID',
  `coupon_id` int NOT NULL COMMENT '优惠券ID',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'unused' COMMENT '使用状态：unused(未使用), used(已使用), expired(已过期)',
  `obtained_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '领取时间',
  `used_at` datetime NULL DEFAULT NULL COMMENT '使用时间',
  `order_id` int NULL DEFAULT NULL COMMENT '使用的订单ID',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_coupon`(`user_id` ASC, `coupon_id` ASC) USING BTREE COMMENT '同一用户同一优惠券只能有一条记录',
  INDEX `idx_user_status`(`user_id` ASC, `status` ASC) USING BTREE,
  INDEX `idx_coupon_status`(`coupon_id` ASC, `status` ASC) USING BTREE,
  INDEX `idx_obtained_at`(`obtained_at` ASC) USING BTREE,
  CONSTRAINT `user_coupons_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `user_coupons_ibfk_2` FOREIGN KEY (`coupon_id`) REFERENCES `coupons` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户优惠券关联表' ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 插入示例数据
-- ============================================

-- 插入示例优惠活动
INSERT INTO `promotion_activities` (`title`, `description`, `activity_type`, `status`, `image_url`, `start_time`, `end_time`, `discount_rate`, `min_purchase_amount`, `total_limit`, `user_limit`) VALUES
('国庆特惠套餐', '国庆期间限时特惠，包含3只豪华滩羊，适合大型聚会', 'package', 'active', '/images/guoqing.jpg', '2024-10-01 00:00:00', '2024-10-07 23:59:59', 0.75, 0, 100, 1),
('春季限时抢购', '春季是滩羊生长的黄金时期，限时抢购享受8折优惠', 'flash_sale', 'active', '/images/spring.jpg', '2024-03-01 00:00:00', '2024-03-31 23:59:59', 0.8, 0, 200, 2),
('满500减80活动', '消费满500元立减80元，更有专业养殖指导服务', 'discount', 'active', NULL, '2024-01-01 00:00:00', '2024-12-31 23:59:59', NULL, 500, NULL, NULL);

-- 插入示例优惠券
INSERT INTO `coupons` (`name`, `code`, `coupon_type`, `status`, `discount_amount`, `min_purchase_amount`, `total_count`, `user_limit`, `valid_from`, `valid_until`, `description`) VALUES
('满200减30', 'MAN200JIAN30', 'discount', 'active', 30, 200, 1000, 1, '2024-01-01 00:00:00', '2024-12-31 23:59:59', '消费满200元可使用，立减30元'),
('满500减80', 'MAN500JIAN80', 'discount', 'active', 80, 500, 500, 1, '2024-01-01 00:00:00', '2024-12-31 23:59:59', '消费满500元可使用，立减80元'),
('9折优惠券', 'DISCOUNT90', 'percentage', 'active', NULL, 100, 2000, 2, '2024-01-01 00:00:00', '2024-12-31 23:59:59', '消费满100元可使用，享受9折优惠，最高优惠50元'),
('10元现金券', 'CASH10', 'cash', 'active', 10, 0, 5000, 3, '2024-01-01 00:00:00', '2024-12-31 23:59:59', '无门槛使用，直接抵扣10元');

