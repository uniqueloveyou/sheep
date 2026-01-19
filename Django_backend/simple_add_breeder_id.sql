-- ----------------------------
-- 简化版：为sheep表添加breeder_id字段，建立关联闭环
-- 
-- 关联闭环：
-- breeders.id <-- sheep.breeder_id (羊只属于哪个养殖户)
-- sheep.id <-- cart_items.sheep_id (购物车中的羊只)
-- 
-- 执行步骤：请分步执行，如果某步报错（如字段已存在），可以跳过
-- ----------------------------

-- 步骤1：添加breeder_id字段
ALTER TABLE `sheep` 
ADD COLUMN `breeder_id` int NULL COMMENT '养殖户ID' AFTER `length`;

-- 步骤2：添加索引
CREATE INDEX `idx_breeder_id` ON `sheep`(`breeder_id`);

-- 步骤3：添加外键约束
ALTER TABLE `sheep` 
ADD CONSTRAINT `sheep_ibfk_breeder` 
FOREIGN KEY (`breeder_id`) REFERENCES `breeders` (`id`) 
ON DELETE SET NULL ON UPDATE RESTRICT;

-- 完成！现在关联关系闭环已建立：
-- breeders (1) <-- (N) sheep (1) <-- (N) cart_items

