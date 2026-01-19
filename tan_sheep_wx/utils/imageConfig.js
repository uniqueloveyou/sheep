/**
 * 图片资源配置文件
 * 统一管理本地图片路径
 */

// 功能图标配置（仅本地路径）
const FUNCTION_ICONS = {
  // 功能入口图标（首页）
  f1: '/images/icons/function/f1.png',        // 定制领养
  f3: '/images/icons/function/f3.png',        // 盐池县地图
  f4: '/images/icons/function/f4.png',        // 优惠活动
  f5: '/images/icons/function/f5-1.png',      // 生长周期（注意文件名是 f5-1）
  f6: '/images/icons/function/f6.png',        // 场地监控
  f7: '/images/icons/function/f7.png',        // 日常饲料
  f8: '/images/icons/function/f8.png',        // 养殖户
  food: '/images/icons/function/food.png',    // 滩羊食谱
}

// 菜单图标配置（我的页面）
const MENU_ICONS = {
  user: '/pages/my/images/user1.png',         // 个人资料
  adopt: '/pages/my/images/lingyang.png',     // 查看领养
  coupon: '/pages/my/images/youhui.png',      // 优惠券
}

/**
 * 获取功能图标路径（仅本地）
 * @param {string} key 图标key (f1, f3, f4, f5, f6, f7, f8, food)
 * @returns {string} 本地图标路径
 */
function getFunctionIcon(key) {
  return FUNCTION_ICONS[key] || ''
}

/**
 * 获取菜单图标路径（仅本地）
 * @param {string} key 图标key (user, adopt, coupon)
 * @returns {string} 本地图标路径
 */
function getMenuIcon(key) {
  return MENU_ICONS[key] || ''
}

module.exports = {
  FUNCTION_ICONS,
  MENU_ICONS,
  getFunctionIcon,
  getMenuIcon,
}

