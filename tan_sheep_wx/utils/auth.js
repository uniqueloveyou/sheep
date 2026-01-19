const WXAPI = require('apifm-wxapi')
const CONFIG = require('../config.js')
const API = require('./api.js')  // 引入自定义API工具
async function checkSession(){
  return new Promise((resolve, reject) => {
    wx.checkSession({
      success() {
        return resolve(true)
      },
      fail() {
        return resolve(false)
      }
    })
  })
}

async function bindSeller() {
  const token = wx.getStorageSync('token')
  const referrer = wx.getStorageSync('referrer')
  if (!token) {
    return
  }
  if (!referrer) {
    return
  }
  const res = await WXAPI.bindSeller({
    token,
    uid: referrer
  })
}

// 检测登录状态，返回 true / false
async function checkHasLogined() {
  const token = wx.getStorageSync('token')
  if (!token) {
    return false
  }
  const loggined = await checkSession()
  if (!loggined) {
    wx.removeStorageSync('token')
    return false
  }
  // 优先使用自定义API验证token
  try {
    const checkTokenRes = await API.checkToken(token)
    if (checkTokenRes.code != 0) {
      wx.removeStorageSync('token')
      return false
    }
    return true
  } catch (error) {
    console.error('自定义API验证token失败，尝试使用WXAPI:', error)
    // 回退到WXAPI
  const checkTokenRes = await WXAPI.checkToken(token)
  if (checkTokenRes.code != 0) {
    wx.removeStorageSync('token')
    return false
  }
  return true
  }
}

async function wxaCode(){
  return new Promise((resolve, reject) => {
    wx.login({
      success(res) {
        return resolve(res.code)
      },
      fail() {
        wx.showToast({
          title: '获取code失败',
          icon: 'none'
        })
        return resolve('获取code失败')
      }
    })
  })
}

async function login(page){
  const _this = this
  wx.login({
    success: function (res) {
      const extConfigSync = wx.getExtConfigSync()
      if (extConfigSync.subDomain) {
        WXAPI.wxappServiceLogin({
          code: res.code
        }).then(function (res) {        
          if (res.code == 10000) {
            // 去注册
            return;
          }
          if (res.code != 0) {
            // 登录错误
            wx.showModal({
              title: '无法登录',
              content: res.msg,
              showCancel: false
            })
            return;
          }
          wx.setStorageSync('token', res.data.token)
          wx.setStorageSync('uid', res.data.uid)
          if (CONFIG.bindSeller) {
            _this.bindSeller()
          }
          if ( page ) {
            page.onShow()
          }
        })
      } else {
        WXAPI.login_wx(res.code).then(function (res) {        
          if (res.code == 10000) {
            // 去注册
            return;
          }
          if (res.code != 0) {
            // 登录错误
            wx.showModal({
              title: '无法登录',
              content: res.msg,
              showCancel: false
            })
            return;
          }
          wx.setStorageSync('token', res.data.token)
          wx.setStorageSync('uid', res.data.uid)
          if (CONFIG.bindSeller) {
            _this.bindSeller()
          }
          if ( page ) {
            page.onShow()
          }
        })
      }
    }
  })
}

async function authorize() {
  // const code = await wxaCode()
  // const resLogin = await WXAPI.login_wx(code)
  // if (resLogin.code == 0) {
  //   wx.setStorageSync('token', resLogin.data.token)
  //   wx.setStorageSync('uid', resLogin.data.uid)
  //   return resLogin
  // }
  return new Promise((resolve, reject) => {
    wx.login({
      success: function (res) {
        const code = res.code
        let referrer = '' // 推荐人
        let referrer_storge = wx.getStorageSync('referrer');
        if (referrer_storge) {
          referrer = referrer_storge;
        }
        // 下面开始调用注册接口
        const extConfigSync = wx.getExtConfigSync()
        if (extConfigSync.subDomain) {
          WXAPI.wxappServiceAuthorize({
            code: code,
            referrer: referrer
          }).then(function (res) {
            if (res.code == 0) {
              wx.setStorageSync('token', res.data.token)
              wx.setStorageSync('uid', res.data.uid)
              resolve(res)
            } else {
              wx.showToast({
                title: res.msg,
                icon: 'none'
              })
              reject(res.msg)
            }
          })
        } else {
          WXAPI.authorize({
            code: code,
            referrer: referrer
          }).then(function (res) {
            if (res.code == 0) {
              wx.setStorageSync('token', res.data.token)
              wx.setStorageSync('uid', res.data.uid)
              resolve(res)
            } else {
              wx.showToast({
                title: res.msg,
                icon: 'none'
              })
              reject(res.msg)
            }
          })
        }
      },
      fail: err => {
        reject(err)
      }
    })
  })
}

// 最新的登陆接口，建议用这个
// 优先使用自定义后端API，如果失败则回退到WXAPI
async function login20241025() {
  console.log('[登录] 开始获取微信code...')
  const code = await wxaCode()
  console.log('[登录] 获取到code:', code ? code.substring(0, 10) + '...' : '失败')
  
  if (!code || code === '获取code失败') {
    throw new Error('获取微信登录code失败')
  }
  
  try {
    console.log('[登录] 调用自定义后端API...')
    // 优先使用自定义后端API
    const res = await API.login(code)
    console.log('[登录] 后端API返回:', res)
    
    if (res.code == 0) {
      // 登录成功
      wx.setStorageSync('token', res.data.token)
      wx.setStorageSync('uid', res.data.uid)
      wx.setStorageSync('openid', res.data.openid || '')
      wx.setStorageSync('mobile', res.data.mobile || '')
      if (CONFIG.bindSeller) {
        this.bindSeller()
      }
      return res
    } else if (res.code == 10000) {
      // 需要注册（但我们的后端已经自动注册了，这里不应该出现）
      return res
    } else {
      // 登录错误
      wx.showModal({
        content: res.msg || '登录失败',
        showCancel: false
      })
      return res
    }
  } catch (error) {
    console.error('[登录] 自定义API登录失败:', error)
    console.error('[登录] 错误详情:', error.message, error.stack)
    
    // 显示更详细的错误信息
    if (error.message && error.message.includes('网络请求失败')) {
      wx.showModal({
        title: '连接失败',
        content: '无法连接到后端服务器\n\n请检查：\n1. 后端服务是否已启动\n2. API地址是否正确\n3. 网络是否正常',
        showCancel: false
      })
    }
    
    console.log('[登录] 尝试使用WXAPI作为备用方案...')
    
    // 如果自定义API失败，回退到WXAPI（兼容旧系统）
  const extConfigSync = wx.getExtConfigSync()
  if (extConfigSync.subDomain) {
    // 服务商模式
    const res = await WXAPI.wxappServiceLogin({ code })
    if (res.code == 10000) {
      return res
    }
    if (res.code != 0) {
      wx.showModal({
        content: res.msg,
        showCancel: false
      })
      return res
    }
    wx.setStorageSync('token', res.data.token)
    wx.setStorageSync('uid', res.data.uid)
    wx.setStorageSync('openid', res.data.openid)
    wx.setStorageSync('mobile', res.data.mobile)
    if (CONFIG.bindSeller) {
      this.bindSeller()
    }
    return res
  } else {
    // 非服务商模式
    const res = await WXAPI.login_wx(code)
    if (res.code == 10000) {
      return res;
    }
    if (res.code != 0) {
      wx.showModal({
        content: res.msg,
        showCancel: false
      })
      return res;
    }
    wx.setStorageSync('token', res.data.token)
    wx.setStorageSync('uid', res.data.uid)
    wx.setStorageSync('openid', res.data.openid)
    wx.setStorageSync('mobile', res.data.mobile)
    if (CONFIG.bindSeller) {
      this.bindSeller()
    }
    return res
    }
  }
}

function loginOut(){
  wx.removeStorageSync('token')
  wx.removeStorageSync('uid')
  wx.removeStorageSync('openid')
  wx.removeStorageSync('mobile')
}

async function checkAndAuthorize (scope) {
  return new Promise((resolve, reject) => {
    wx.getSetting({
      success(res) {
        if (!res.authSetting[scope]) {
          wx.authorize({
            scope: scope,
            success() {
              resolve() // 无返回参数
            },
            fail(e){
              console.error(e)
              // if (e.errMsg.indexof('auth deny') != -1) {
              //   wx.showToast({
              //     title: e.errMsg,
              //     icon: 'none'
              //   })
              // }
              wx.showModal({
                title: '无权操作',
                content: '需要获得您的授权',
                showCancel: false,
                confirmText: '立即授权',
                confirmColor: '#e64340',
                success(res) {
                  wx.openSetting();
                },
                fail(e){
                  console.error(e)
                  reject(e)
                },
              })
            }
          })
        } else {
          resolve() // 无返回参数
        }
      },
      fail(e){
        console.error(e)
        reject(e)
      }
    })
  })  
}

module.exports = {
  checkHasLogined: checkHasLogined,
  wxaCode: wxaCode,
  login: login,
  login20241025: login20241025,
  loginOut: loginOut,
  checkAndAuthorize: checkAndAuthorize,
  authorize: authorize,
  bindSeller: bindSeller
}