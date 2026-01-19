-- ============================================
-- 向 breeders 表插入养殖户信息
-- ============================================

-- 方式1：插入单条记录（不指定id，使用自增）
-- 注意：需要先执行 add_breeder_location_fields.sql 添加位置字段
INSERT INTO `breeders` (`name`, `gender`, `phone`, `sheep_count`, `sheep_id`, `female_count`, `male_count`, `latitude`, `longitude`, `address`) 
VALUES ('赵红', '女', '13800138001', 50, 'X45678901', 30, 20, 37.785595, 107.41541, '宁夏回族自治区盐池县某镇某村');

-- 方式2：插入多条记录（批量插入，包含位置信息）
INSERT INTO `breeders` (`name`, `gender`, `phone`, `sheep_count`, `sheep_id`, `female_count`, `male_count`, `latitude`, `longitude`, `address`) 
VALUES 
    ('刘明', '男', '13800138002', 75, 'X45678902', 40, 35, 37.783595, 107.39541, '宁夏回族自治区盐池县某镇某村'),
    ('陈芳', '女', '13800138003', 90, 'X45678903', 50, 40, 37.787595, 107.40541, '宁夏回族自治区盐池县某镇某村'),
    ('张伟', '男', '13800138004', 60, 'X45678904', 35, 25, 37.784595, 107.42541, '宁夏回族自治区盐池县某镇某村'),
    ('王丽', '女', '13800138005', 110, 'X45678905', 60, 50, 37.786595, 107.41541, '宁夏回族自治区盐池县某镇某村');

-- 方式3：如果指定id（需要确保id不存在）
INSERT INTO `breeders` (`id`, `name`, `gender`, `phone`, `sheep_count`, `sheep_id`, `female_count`, `male_count`, `latitude`, `longitude`, `address`) 
VALUES (10, '孙强', '男', '13800138006', 85, 'X45678906', 45, 40, 37.788595, 107.43541, '宁夏回族自治区盐池县某镇某村');

-- 方式4：使用 INSERT IGNORE（如果sheep_id已存在则忽略，不会报错）
INSERT IGNORE INTO `breeders` (`name`, `gender`, `phone`, `sheep_count`, `sheep_id`, `female_count`, `male_count`, `latitude`, `longitude`, `address`) 
VALUES ('周敏', '女', '13800138007', 95, 'X45678907', 50, 45, 37.782595, 107.38541, '宁夏回族自治区盐池县某镇某村');

-- 方式5：使用 REPLACE（如果sheep_id已存在则替换）
REPLACE INTO `breeders` (`name`, `gender`, `phone`, `sheep_count`, `sheep_id`, `female_count`, `male_count`, `latitude`, `longitude`, `address`) 
VALUES ('吴刚', '男', '13800138008', 70, 'X45678908', 38, 32, 37.789595, 107.44541, '宁夏回族自治区盐池县某镇某村');

-- ============================================
-- 字段说明：
-- name: 姓名（必填，varchar(100)）
-- gender: 性别（必填，'男' 或 '女'）
-- phone: 联系电话（必填，varchar(20)）
-- sheep_count: 羊只总数（必填，int）
-- sheep_id: 羊只编号（必填，varchar(50)，唯一）
-- female_count: 母羊数量（必填，int）
-- male_count: 公羊数量（必填，int）
-- latitude: 纬度（可选，decimal(10,7)，用于地图显示）
-- longitude: 经度（可选，decimal(10,7)，用于地图显示）
-- address: 地址（可选，varchar(200)，详细地址）
-- ============================================

-- 注意事项：
-- 1. sheep_id 字段是唯一的，不能重复
-- 2. sheep_count 应该等于 female_count + male_count
-- 3. 如果不指定 id，数据库会自动分配自增ID
-- 4. 建议使用方式1或方式2进行插入
-- 5. 位置信息（latitude, longitude）用于地图功能，如果不需要可以设为NULL
-- 6. 坐标格式：纬度范围 -90 到 90，经度范围 -180 到 180
-- 7. 盐池县大致坐标：纬度 37.784595, 经度 107.40541

