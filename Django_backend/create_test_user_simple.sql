-- ============================================
-- 创建测试用户（简化版）
-- ============================================
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 删除已存在的测试用户（如果存在）
DELETE FROM `users` WHERE `username` IN ('admin', 'test', 'user1');

-- 插入测试用户
-- 注意：MySQL不支持 || 作为字符串连接，使用CONCAT函数
INSERT INTO `users` (`username`, `password`, `openid`, `nickname`, `mobile`, `gender`, `created_at`, `updated_at`) 
VALUES 
('admin', 'admin123', CONCAT('test_openid_admin_', UNIX_TIMESTAMP()), '管理员', '13800138000', 1, NOW(), NOW()),
('test', 'test123', CONCAT('test_openid_test_', UNIX_TIMESTAMP()), '测试用户', '13900139000', 0, NOW(), NOW()),
('user1', '123456', CONCAT('test_openid_user1_', UNIX_TIMESTAMP()), '用户1', '13700137000', 1, NOW(), NOW());

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 测试账号
-- ============================================
-- 用户名: admin, 密码: admin123
-- 用户名: test, 密码: test123  
-- 用户名: user1, 密码: 123456

