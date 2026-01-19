-- ============================================
-- 为 sheep 表添加缺失的字段
-- ============================================
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 步骤1：添加 name 字段（羊只名称/编号）
ALTER TABLE `sheep` 
ADD COLUMN `name` VARCHAR(100) NULL COMMENT '羊只名称/编号' AFTER `id`;

-- 步骤2：添加 birth_date 字段（出生日期）
ALTER TABLE `sheep` 
ADD COLUMN `birth_date` DATE NULL COMMENT '出生日期' AFTER `name`;

-- 步骤3：添加 price 字段（价格）
ALTER TABLE `sheep` 
ADD COLUMN `price` DECIMAL(10, 2) NULL DEFAULT 0.00 COMMENT '价格（元）' AFTER `breeder_id`;

-- 步骤4：添加 image_url 字段（图片URL）
ALTER TABLE `sheep` 
ADD COLUMN `image_url` VARCHAR(500) NULL COMMENT '图片URL' AFTER `price`;

-- 步骤5：添加 status 字段（状态）
ALTER TABLE `sheep` 
ADD COLUMN `status` VARCHAR(20) NULL DEFAULT 'available' COMMENT '状态：available(待售), sold(已售), reserved(已预订), unavailable(不可售)' AFTER `image_url`;

-- 步骤6：添加 description 字段（描述）
ALTER TABLE `sheep` 
ADD COLUMN `description` TEXT NULL COMMENT '描述信息' AFTER `status`;

-- 步骤7：添加 created_at 和 updated_at 字段（时间戳）
ALTER TABLE `sheep` 
ADD COLUMN `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间' AFTER `description`;

ALTER TABLE `sheep` 
ADD COLUMN `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间' AFTER `created_at`;

-- 步骤8：添加索引
CREATE INDEX `idx_status` ON `sheep`(`status`);
CREATE INDEX `idx_price` ON `sheep`(`price`);
CREATE INDEX `idx_birth_date` ON `sheep`(`birth_date`);

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 说明：
-- 1. name: 羊只名称/编号，方便识别和搜索
-- 2. birth_date: 出生日期，用于计算年龄，在生长周期功能中很有用
-- 3. price: 价格，购物车和购买功能必需
-- 4. image_url: 图片URL，用于展示羊只图片
-- 5. status: 状态，用于管理羊只的销售状态
-- 6. description: 描述信息，可以包含羊只的详细信息
-- 7. created_at/updated_at: 时间戳，用于记录创建和更新时间
-- ============================================

