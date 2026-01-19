-- ============================================
-- 地图功能测试数据
-- 用于快速测试地图功能是否正常
-- ============================================

-- 1. 首先确保字段已添加（如果已添加会报错，可以忽略）
ALTER TABLE `breeders` 
ADD COLUMN IF NOT EXISTS `latitude` decimal(10, 7) NULL COMMENT '纬度' AFTER `male_count`;

ALTER TABLE `breeders` 
ADD COLUMN IF NOT EXISTS `longitude` decimal(10, 7) NULL COMMENT '经度' AFTER `latitude`;

ALTER TABLE `breeders` 
ADD COLUMN IF NOT EXISTS `address` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '地址' AFTER `longitude`;

-- 2. 为现有数据添加位置信息（盐池县附近的坐标）
UPDATE `breeders` SET 
  `latitude` = 37.785595, 
  `longitude` = 107.41541,
  `address` = '宁夏回族自治区盐池县某镇某村'
WHERE `id` = 1 AND (`latitude` IS NULL OR `longitude` IS NULL);

UPDATE `breeders` SET 
  `latitude` = 37.783595, 
  `longitude` = 107.39541,
  `address` = '宁夏回族自治区盐池县某镇某村'
WHERE `id` = 2 AND (`latitude` IS NULL OR `longitude` IS NULL);

UPDATE `breeders` SET 
  `latitude` = 37.787595, 
  `longitude` = 107.40541,
  `address` = '宁夏回族自治区盐池县某镇某村'
WHERE `id` = 3 AND (`latitude` IS NULL OR `longitude` IS NULL);

-- 3. 插入测试数据（如果现有数据不足）
INSERT IGNORE INTO `breeders` 
(`name`, `gender`, `phone`, `sheep_count`, `sheep_id`, `female_count`, `male_count`, `latitude`, `longitude`, `address`) 
VALUES 
('测试养殖户1', '男', '13800138001', 50, 'TEST001', 25, 25, 37.784595, 107.40541, '宁夏回族自治区盐池县测试地址1'),
('测试养殖户2', '女', '13800138002', 60, 'TEST002', 30, 30, 37.786595, 107.41541, '宁夏回族自治区盐池县测试地址2'),
('测试养殖户3', '男', '13800138003', 70, 'TEST003', 35, 35, 37.782595, 107.39541, '宁夏回族自治区盐池县测试地址3');

-- 4. 验证数据
SELECT 
  id, 
  name, 
  latitude, 
  longitude, 
  address,
  CASE 
    WHEN latitude IS NULL OR longitude IS NULL THEN '缺少位置信息'
    ELSE '有位置信息'
  END AS location_status
FROM `breeders`
ORDER BY id;

-- 5. 统计有位置信息的养殖户数量
SELECT 
  COUNT(*) AS total_breeders,
  SUM(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 ELSE 0 END) AS with_location,
  SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) AS without_location
FROM `breeders`;


