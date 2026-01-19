-- ----------------------------
-- 修正表关联关系，形成闭环
-- 关系说明：
-- 1. breeders.id (养殖户ID) <-- sheep.breeder_id (羊只属于哪个养殖户)
-- 2. sheep.id (羊只ID) <-- cart_items.sheep_id (购物车中的羊只)
-- 3. breeders.sheep_id 字段是"羊只编号"（业务编号，如X12345678），不是用来关联的
-- ----------------------------
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 步骤1：为sheep表添加breeder_id字段（如果还没有）
ALTER TABLE `sheep` 
ADD COLUMN `breeder_id` int NULL COMMENT '养殖户ID' AFTER `length`;

-- 步骤2：添加索引
CREATE INDEX `idx_breeder_id` ON `sheep`(`breeder_id`);

-- 步骤3：添加外键约束（sheep.breeder_id -> breeders.id）
ALTER TABLE `sheep` 
ADD CONSTRAINT `sheep_ibfk_breeder` 
FOREIGN KEY (`breeder_id`) REFERENCES `breeders` (`id`) 
ON DELETE SET NULL ON UPDATE RESTRICT;

-- 步骤4：确保cart_items表的外键正确（sheep_id -> sheep.id）
-- 注意：如果cart_items表已经存在，检查外键是否正确
-- 如果外键不存在，添加它：
ALTER TABLE `cart_items` 
ADD CONSTRAINT `cart_items_ibfk_sheep` 
FOREIGN KEY (`sheep_id`) REFERENCES `sheep` (`id`) 
ON DELETE CASCADE ON UPDATE RESTRICT;

SET FOREIGN_KEY_CHECKS = 1;

-- 关联关系说明：
-- breeders (1) <-- (N) sheep (1) <-- (N) cart_items
-- 一个养殖户可以有多只羊
-- 一只羊可以出现在多个购物车中（不同用户）

-- 可选：如果已有数据，可以手动更新关联关系
-- 例如：将羊只1关联到养殖户1
-- UPDATE `sheep` SET `breeder_id` = 1 WHERE `id` = 1;
-- UPDATE `sheep` SET `breeder_id` = 2 WHERE `id` = 2;
-- UPDATE `sheep` SET `breeder_id` = 3 WHERE `id` = 3;

