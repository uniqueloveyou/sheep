-- ============================================
-- 为 breeders 表添加位置信息字段
-- ============================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 添加纬度字段
ALTER TABLE `breeders` 
ADD COLUMN `latitude` decimal(10, 7) NULL COMMENT '纬度' AFTER `male_count`;

-- 添加经度字段
ALTER TABLE `breeders` 
ADD COLUMN `longitude` decimal(10, 7) NULL COMMENT '经度' AFTER `latitude`;

-- 添加地址字段
ALTER TABLE `breeders` 
ADD COLUMN `address` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '地址' AFTER `longitude`;

-- 添加位置索引（用于地理位置查询）
ALTER TABLE `breeders` 
ADD INDEX `idx_location`(`latitude`, `longitude`) USING BTREE;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 示例：更新现有数据的坐标（盐池县附近的坐标）
-- ============================================
-- 盐池县中心坐标大约：纬度 37.784595, 经度 107.40541

-- 更新示例数据（根据实际情况修改）
-- UPDATE `breeders` SET 
--   `latitude` = 37.785595, 
--   `longitude` = 107.41541,
--   `address` = '宁夏回族自治区盐池县某镇某村'
-- WHERE `id` = 1;

-- UPDATE `breeders` SET 
--   `latitude` = 37.783595, 
--   `longitude` = 107.39541,
--   `address` = '宁夏回族自治区盐池县某镇某村'
-- WHERE `id` = 2;

-- UPDATE `breeders` SET 
--   `latitude` = 37.787595, 
--   `longitude` = 107.40541,
--   `address` = '宁夏回族自治区盐池县某镇某村'
-- WHERE `id` = 3;

