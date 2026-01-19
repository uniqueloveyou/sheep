-- ----------------------------
-- 为sheep表添加breeder_id字段，关联breeders表
-- ----------------------------
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 添加breeder_id字段
ALTER TABLE `sheep` 
ADD COLUMN `breeder_id` int NULL COMMENT '养殖户ID' AFTER `length`;

-- 添加索引
ALTER TABLE `sheep` 
ADD INDEX `idx_breeder_id`(`breeder_id` ASC) USING BTREE;

-- 添加外键约束
ALTER TABLE `sheep` 
ADD CONSTRAINT `sheep_ibfk_breeder` FOREIGN KEY (`breeder_id`) REFERENCES `breeders` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT;

SET FOREIGN_KEY_CHECKS = 1;

-- 可选：如果已有数据，可以手动更新关联关系
-- UPDATE `sheep` SET `breeder_id` = 1 WHERE `id` = 1;
-- UPDATE `sheep` SET `breeder_id` = 2 WHERE `id` = 2;
-- UPDATE `sheep` SET `breeder_id` = 3 WHERE `id` = 3;

