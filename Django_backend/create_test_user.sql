-- ============================================
-- 创建测试用户
-- ============================================
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 注意：users表要求openid是唯一的且必填
-- 如果表中已有数据，请先检查

-- 先删除已存在的测试用户（避免冲突）
DELETE FROM `users` WHERE `username` IN ('admin', 'test', 'user1');

-- 插入测试用户（账号密码登录）
INSERT INTO `users` (`username`, `password`, `openid`, `nickname`, `mobile`, `gender`, `created_at`, `updated_at`) 
VALUES 
('admin', 'admin123', CONCAT('test_openid_admin_', UNIX_TIMESTAMP()), '管理员', '13800138000', 1, NOW(), NOW()),
('test', 'test123', CONCAT('test_openid_test_', UNIX_TIMESTAMP()), '测试用户', '13900139000', 0, NOW(), NOW()),
('user1', '123456', CONCAT('test_openid_user1_', UNIX_TIMESTAMP()), '用户1', '13700137000', 1, NOW(), NOW());

-- 或者如果表是空的，可以直接插入（不需要ON DUPLICATE KEY UPDATE）
-- 先检查是否有数据
-- SELECT COUNT(*) FROM `users` WHERE `username` IN ('admin', 'test', 'user1');

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 测试账号说明
-- ============================================
-- 用户名: admin, 密码: admin123
-- 用户名: test, 密码: test123
-- 用户名: user1, 密码: 123456

