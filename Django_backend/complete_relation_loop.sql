-- ----------------------------
-- 建立完整的表关联关系闭环
-- 
-- 关联关系：
-- breeders.id (1) <-- sheep.breeder_id (N) 
-- sheep.id (1) <-- cart_items.sheep_id (N)
-- 
-- 说明：
-- 1. 一个养殖户可以有多只羊（通过sheep.breeder_id关联）
-- 2. 一只羊可以出现在多个购物车中（通过cart_items.sheep_id关联）
-- 3. sheep.id 是核心，所有关联都指向它
-- ----------------------------
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 步骤1：为sheep表添加breeder_id字段
-- ============================================
-- 如果字段已存在，会报错，可以忽略
ALTER TABLE `sheep` 
ADD COLUMN `breeder_id` int NULL COMMENT '养殖户ID' AFTER `length`;

-- ============================================
-- 步骤2：添加索引
-- ============================================
-- MySQL 8.0+ 支持 IF NOT EXISTS，旧版本如果索引已存在会报错
CREATE INDEX `idx_breeder_id` ON `sheep`(`breeder_id`);

-- ============================================
-- 步骤3：添加外键约束（sheep.breeder_id -> breeders.id）
-- ============================================
-- 先检查并删除可能存在的同名约束（如果存在）
SET @constraint_exists = (
    SELECT COUNT(*) 
    FROM information_schema.TABLE_CONSTRAINTS 
    WHERE CONSTRAINT_SCHEMA = DATABASE() 
    AND TABLE_NAME = 'sheep' 
    AND CONSTRAINT_NAME = 'sheep_ibfk_breeder'
);

SET @sql = IF(@constraint_exists > 0, 
    'ALTER TABLE `sheep` DROP FOREIGN KEY `sheep_ibfk_breeder`', 
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加外键约束
ALTER TABLE `sheep` 
ADD CONSTRAINT `sheep_ibfk_breeder` 
FOREIGN KEY (`breeder_id`) REFERENCES `breeders` (`id`) 
ON DELETE SET NULL ON UPDATE RESTRICT;

-- ============================================
-- 步骤4：确保cart_items表的外键正确
-- ============================================
-- cart_items.sheep_id 应该已经关联到 sheep.id
-- 如果外键不存在，添加它（cart_items表创建时应该已经有了）

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 验证关联关系闭环的SQL查询
-- ============================================

-- 查询1：通过羊只查看所属养殖户
-- SELECT 
--     s.id as sheep_id,
--     s.gender,
--     s.weight,
--     b.id as breeder_id,
--     b.name as breeder_name,
--     b.phone as breeder_phone
-- FROM sheep s
-- LEFT JOIN breeders b ON s.breeder_id = b.id;

-- 查询2：通过购物车查看羊只和养殖户信息
-- SELECT 
--     ci.id as cart_item_id,
--     ci.quantity,
--     ci.price,
--     s.id as sheep_id,
--     s.gender,
--     s.weight,
--     b.id as breeder_id,
--     b.name as breeder_name
-- FROM cart_items ci
-- JOIN sheep s ON ci.sheep_id = s.id
-- LEFT JOIN breeders b ON s.breeder_id = b.id;

-- 查询3：通过养殖户查看所有羊只
-- SELECT 
--     b.id as breeder_id,
--     b.name as breeder_name,
--     s.id as sheep_id,
--     s.gender,
--     s.weight,
--     COUNT(ci.id) as in_cart_count
-- FROM breeders b
-- LEFT JOIN sheep s ON s.breeder_id = b.id
-- LEFT JOIN cart_items ci ON ci.sheep_id = s.id
-- GROUP BY b.id, s.id;

-- ============================================
-- 可选：更新已有数据的关联关系
-- ============================================
-- 如果已有数据，可以手动更新关联关系
-- 例如：将羊只1关联到养殖户1，羊只2关联到养殖户2，羊只3关联到养殖户3
-- UPDATE `sheep` SET `breeder_id` = 1 WHERE `id` = 1;
-- UPDATE `sheep` SET `breeder_id` = 2 WHERE `id` = 2;
-- UPDATE `sheep` SET `breeder_id` = 3 WHERE `id` = 3;

