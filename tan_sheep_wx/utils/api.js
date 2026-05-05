/**
 * API璇锋眰宸ュ叿
 * 鐩存帴璋冪敤鍚庣API
 */

// 鍚庣API鍦板潃閰嶇疆
const {
  getApiBaseUrl,
  getApiBaseUrlCandidates,
  rememberApiBaseUrl
} = require('./api-config.js')

function normalizeEarTag(earTag) {
  return String(earTag || '').trim()
}

function isValidEarTag(earTag) {
  return /^[A-Za-z0-9_-]{1,50}$/.test(normalizeEarTag(earTag))
}

function getHostFromUrl(url) {
  const match = String(url || '').match(/^https?:\/\/([^/:]+)/i)
  return match ? match[1] : ''
}

function isLoopbackHost(host) {
  return host === '127.0.0.1' || host === 'localhost'
}

function isPrivateNetworkHost(host) {
  return /^10\./.test(host)
    || /^192\.168\./.test(host)
    || /^172\.(1[6-9]|2\d|3[01])\./.test(host)
}

function isRetriableStatus(statusCode) {
  return statusCode === 502 || statusCode === 503 || statusCode === 504
}

function formatResponseErrorData(data) {
  if (data && data.msg) {
    return data.msg
  }
  if (typeof data === 'string') {
    if (data.indexOf('Error code 502') !== -1 || data.indexOf('Bad gateway') !== -1) {
      return '服务器网关异常，请确认后端服务是否已启动'
    }
    return data.length > 120 ? data.slice(0, 120) + '...' : data
  }
  return ''
}

function getResolvedApiBaseUrl() {
  return getApiBaseUrl()
}

function buildFullUrl(url, baseUrl) {
  return (baseUrl || getResolvedApiBaseUrl()) + url
}

function createRequestFailError(fullUrl, err) {
  const errMsg = err && err.errMsg ? err.errMsg : '未知错误'
  const host = getHostFromUrl(fullUrl)
  const triedUrls = err && err.triedUrls ? err.triedUrls : [fullUrl]
  let message = `网络请求失败: ${errMsg}`

  if (isLoopbackHost(host)) {
    message += `。当前接口地址 ${fullUrl} 指向的是当前设备自身，不一定是开发电脑。如果你在真机上调试，请改成开发电脑局域网 IP，并用 python manage.py runserver 0.0.0.0:8000 启动后端。`
  } else if (isPrivateNetworkHost(host)) {
    message += `。当前接口地址为 ${fullUrl}。如果仍然无法访问，请确认 Django 已用 python manage.py runserver 0.0.0.0:8000 启动，并检查开发者工具里的合法域名校验设置。`
  }

  if (triedUrls.length > 1) {
    message += `。已尝试: ${triedUrls.join('、')}`
  }

  const error = new Error(message)
  error.errMsg = errMsg
  error.url = fullUrl
  error.triedUrls = triedUrls
  return error
}

/**
 * 鍙戣捣璇锋眰
 */
function requestOnce(fullUrl, method, data) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: fullUrl,
      method: method,
      data: data,
      header: {
        'Content-Type': 'application/json'
      },
      success: function (res) {
        resolve(res)
      },
      fail: function (err) {
        reject(err)
      }
    })
  })
}

/**
 * 鍙戣捣璇锋眰
 */
function request(url, method = 'GET', data = {}) {
  const baseUrls = getApiBaseUrlCandidates()
  const triedUrls = []

  function attempt(index) {
    const baseUrl = baseUrls[index] || getResolvedApiBaseUrl()
    const fullUrl = buildFullUrl(url, baseUrl)
    triedUrls.push(fullUrl)
    console.log(`[API璇锋眰] ${method} ${fullUrl}`, data)

    return requestOnce(fullUrl, method, data)
      .then(function (res) {
        console.log(`[API鍝嶅簲] ${fullUrl}`, res)

        if (res.statusCode === 200) {
          rememberApiBaseUrl(baseUrl)
          return res.data
        }

        let errorMsg = `璇锋眰澶辫触: HTTP ${res.statusCode}`
        const responseMsg = formatResponseErrorData(res.data)
        if (responseMsg) {
          errorMsg = responseMsg
        }
        const error = new Error(errorMsg)
        error.statusCode = res.statusCode
        error.response = res.data
        error.fullUrl = fullUrl
        console.error('[API閿欒]', error.message, {
          statusCode: res.statusCode,
          url: fullUrl
        })
        throw error
      })
      .catch(function (err) {
        if (err && typeof err.statusCode === 'number') {
          if (isRetriableStatus(err.statusCode) && index + 1 < baseUrls.length) {
            return attempt(index + 1)
          }
          throw err
        }

        console.error('[API璇锋眰澶辫触]', fullUrl, err)
        if (index + 1 < baseUrls.length) {
          return attempt(index + 1)
        }
        err.triedUrls = triedUrls
        throw createRequestFailError(fullUrl, err)
      })
  }

  return attempt(0)
}

/**
 * 寰俊鐧诲綍锛堜粎浣跨敤 code锛屼笉鑾峰彇鎵嬫満鍙凤級
 * @param {string} code 寰俊鐧诲綍code
 */
function login(code) {
  return request('/api/auth/login', 'POST', { code })
}

/**
 * 鎵嬫満鍙风櫥褰曪紙寰俊灏忕▼搴忎竴閿櫥褰曪級
 * @param {string} code 寰俊鐧诲綍code锛堢敤浜庢崲鍙杘penid锛?
 * @param {string} phoneCode 鎵嬫満鍙锋巿鏉僣ode锛堢敤浜庤В瀵嗘墜鏈哄彿锛?
 */
function loginWithPhone(data) {
  return request('/api/auth/login_by_phone', 'POST', {
    code: data.code,
    phoneCode: data.phoneCode
  })
}

/**
 * 璐﹀彿瀵嗙爜鐧诲綍
 * @param {string} username 鐢ㄦ埛鍚?
 * @param {string} password 瀵嗙爜
 */
function loginWithPassword(username, password) {
  return request('/api/auth/login_password', 'POST', { username: username, password: password })
}

/**
 * 鐢ㄦ埛娉ㄥ唽
 * @param {string} username 鐢ㄦ埛鍚?
 * @param {string} password 瀵嗙爜
 * @param {string} mobile 鎵嬫満鍙凤紙鍙€夛級
 * @param {string} nickname 鏄电О锛堝彲閫夛級
 */
function register(username, password, mobile, nickname) {
  var data = {
    username: username,
    password: password
  };
  if (mobile) {
    data.mobile = mobile;
  }
  if (nickname) {
    data.nickname = nickname;
  }
  return request('/api/auth/register', 'POST', data)
}

/**
 * 楠岃瘉token
 * @param {string} token 
 */
function checkToken(token) {
  return request('/check_token', 'POST', { token })
}

/**
 * 鑾峰彇鐢ㄦ埛鍩虹淇℃伅
 * @param {string} token 
 */
function getUserInfo(token) {
  return request('/api/user/info?token=' + token, 'GET')
}

/**
 * 浣欓鍏呭€?
 * @param {string} token
 * @param {number} amount 鍏呭€奸噾棰?
 */
function recharge(token, amount) {
  return request('/api/user/recharge', 'POST', { token, amount })
}

/**
 * 鑾峰彇璇︾粏鐢ㄦ埛璧勬枡锛堝惈绠€浠嬬瓑锛?
 * @param {string} token 
 */
function getUserProfile(token) {
  return request('/api/user/profile?token=' + token, 'GET')
}

/**
 * 鏇存柊鐢ㄦ埛璇︾粏璧勬枡
 * @param {string} token 
 * @param {object} data (nickname, gender, mobile, description, birthday)
 */
function updateUserInfo(token, data) {
  // 淇濇寔鍚戝墠鍏煎鏃у彧浼?nickname 鐨勬儏鍐?
  let postData = { token: token }
  if (typeof data === 'string') {
    postData.nickname = data
  } else {
    postData = { ...postData, ...data }
  }
  return request('/api/user/profile_update', 'POST', postData)
}

/**
 * 鐢宠鎴愪负鍏绘畺鎴?
 * @param {string} token 
 * @param {string} mobile 
 */
function applyBreeder(token, mobile) {
  return request('/api/user/apply_breeder', 'POST', {
    token: token,
    mobile: mobile
  })
}

/**
 * 鑾峰彇璐墿杞﹀垪琛?
 * @param {string} token 
 */
function getCart(token) {
  // 閫氳繃璇锋眰澶翠紶閫抰oken锛堟洿瀹夊叏锛?
  const fullUrl = buildFullUrl('/api/cart')
  console.log(`[API璇锋眰] GET ${fullUrl}`, { token: token ? '***' : 'missing' })

  return new Promise((resolve, reject) => {
    wx.request({
      url: fullUrl,
      method: 'GET',
      data: { token: token },
      header: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      success: function (res) {
        console.log(`[API鍝嶅簲] ${fullUrl}`, res)
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          const error = new Error(`璇锋眰澶辫触: HTTP ${res.statusCode}`)
          console.error('[API閿欒]', error.message, res)
          reject(error)
        }
      },
      fail: function (err) {
        console.error('[API璇锋眰澶辫触]', fullUrl, err)
        reject(createRequestFailError(fullUrl, err))
      }
    })
  })
}

/**
 * 娣诲姞鍟嗗搧鍒拌喘鐗╄溅
 * @param {string} token 
 * @param {number} sheepId 缇婂彧ID
 * @param {number} quantity 鏁伴噺锛堝彲閫夛紝榛樿1锛?
 * @param {number} price 鍗曚环锛堝彲閫夛紝浼氭牴鎹綋閲嶈嚜鍔ㄨ绠楋級
 */
function addToCart(token, sheepId, quantity = 1, price = 0) {
  return request('/api/cart', 'POST', {
    token: token,
    sheep_id: sheepId,
    quantity: quantity,
    price: price
  })
}

/**
 * 鍒犻櫎璐墿杞﹀晢鍝?
 * @param {string} token 
 * @param {number} cartItemId 璐墿杞﹀晢鍝両D
 */
function removeFromCart(token, cartItemId) {
  return request(`/api/cart/${cartItemId}?token=${encodeURIComponent(token)}`, 'DELETE')
}

/**
 * 鏇存柊璐墿杞﹀晢鍝佹暟閲?
 * @param {string} token 
 * @param {number} cartItemId 璐墿杞﹀晢鍝両D
 * @param {number} quantity 鏂版暟閲?
 */
function updateCartItem(token, cartItemId, quantity) {
  return request(`/api/cart/${cartItemId}?token=${encodeURIComponent(token)}`, 'PUT', {
    token: token,
    quantity: quantity
  })
}

/**
 * 鑾峰彇澶村儚涓婁紶棰勭鍚?URL
 * @param {string} token 
 * @param {string} fileExt 鏂囦欢鎵╁睍鍚嶏紝濡?.jpg
 * @param {string} contentType MIME 绫诲瀷
 */
function getAvatarUploadUrl(token, fileExt, contentType) {
  return request('/api/user/avatar/upload-url', 'POST', {
    token: token,
    file_ext: fileExt || '.jpg',
    content_type: contentType || 'image/jpeg'
  })
}

/**
 * 纭澶村儚涓婁紶瀹屾垚
 * @param {string} token 
 * @param {string} objectKey R2 涓殑瀵硅薄 key
 */
function confirmAvatarUpload(token, objectKey) {
  return request('/api/user/avatar/confirm', 'POST', {
    token: token,
    object_key: objectKey
  })
}

/**
 * 璐墿杞︾粨绠楋紙鐢熸垚璁㈠崟锛?
 * @param {string} token 
 * @param {string} paymentMethod 鏀粯鏂瑰紡锛?balance' 鎴?'wechat'锛?
 * @param {object} addressInfo { receiver_name, receiver_phone, shipping_address }
 * @param {number} userCouponId 鐢ㄦ埛浼樻儬鍒窱D锛堝彲閫夛級
 * @param {number[]} selectedCartItemIds
 */
function checkout(token, paymentMethod = 'balance', addressInfo = {}, userCouponId = null, selectedCartItemIds = []) {
  const data = {
    token: token,
    payment_method: paymentMethod,
    ...addressInfo
  };
  if (userCouponId) {
    data.user_coupon_id = userCouponId;
  }
  if (Array.isArray(selectedCartItemIds) && selectedCartItemIds.length > 0) {
    data.selected_cart_item_ids = selectedCartItemIds
  }
  return request('/api/cart/checkout', 'POST', data)
}

/**
 * 鑾峰彇鐢ㄦ埛宸茶喘涔扮殑缇婏紙缁撶畻鍚庣殑锛?
 * @param {string} token 
 */
function getMySheep(token) {
  return request('/api/my/sheep?token=' + token, 'GET')
}

/**
 * 获取我的羊溯源更新摘要
 * @param {string} token
 */
function getMySheepUpdates(token) {
  return request('/api/my/sheep/updates?token=' + token, 'GET')
}

/**
 * 鑾峰彇鐢ㄦ埛璁㈠崟鍘嗗彶
 * @param {string} token 
 */
function getOrderHistory(token) {
  return request('/api/orders?token=' + token, 'GET')
}

function requestEndAdoption(token, orderId, deliveryInfo = {}) {
  return request(`/api/orders/${orderId}/request-end`, 'POST', {
    token: token,
    ...deliveryInfo
  })
}

function payCareFee(token, orderId, paymentMethod = 'balance') {
  return request(`/api/orders/${orderId}/pay-care-fee`, 'POST', {
    token: token,
    payment_method: paymentMethod
  })
}

/**
 * 鑾峰彇浼樻儬娲诲姩鍒楄〃
 */
function getPromotionActivities(status) {
  var url = '/api/promotions/activities'
  if (status) {
    url += '?status=' + status
  }
  return request(url, 'GET')
}

/**
 * 鑾峰彇鍙鍙栫殑浼樻儬鍒稿垪琛?
 */
function getAvailableCoupons() {
  return request('/api/promotions/coupons', 'GET')
}

/**
 * 鑾峰彇鐢ㄦ埛宸查鍙栫殑浼樻儬鍒?
 */
function getUserCoupons(token) {
  return request('/api/promotions/coupons?token=' + token, 'GET')
}

/**
 * 棰嗗彇浼樻儬鍒?
 */
function claimCoupon(token, couponId) {
  return request('/api/promotions/coupons/claim', 'POST', {
    token: token,
    coupon_id: couponId
  })
}

/**
 * 鑾峰彇鍙鐞嗙殑鍏绘畺鎴峰垪琛紙鐩戞帶锛?
 * @param {string} token
 */
function getMonitorBreeders(token) {
  return request('/api/monitor/breeders?token=' + encodeURIComponent(token), 'GET')
}

/**
 * 鑾峰彇鐩戞帶璁惧鍒楄〃
 * @param {string} token
 * @param {number|string} breederId
 */
function getMonitorDevices(token, breederId) {
  let url = '/api/monitor/devices?token=' + encodeURIComponent(token)
  if (breederId) {
    url += '&breeder_id=' + encodeURIComponent(breederId)
  }
  return request(url, 'GET')
}

/**
 * 鑾峰彇棣栭〉璧勮锛堝浐瀹?鏉★級
 */
function getHomeNews() {
  return request('/api/news/home', 'GET')
}

/**
 * 鑾峰彇璧勮璇︽儏
 * @param {number|string} newsId
 */
function getNewsDetail(newsId) {
  return request(`/api/news/${newsId}`, 'GET')
}

/**
 * 鑾峰彇璧勮鍒楄〃
 * @param {number} page
 * @param {number} pageSize
 */
function getNewsList(page = 1, pageSize = 10) {
  return request(`/api/news/list?page=${page}&page_size=${pageSize}`, 'GET')
}

const api = {
  request,
  normalizeEarTag,
  isValidEarTag,
  getApiBaseUrl: getResolvedApiBaseUrl,
  login,
  loginWithPhone,
  loginWithPassword,
  register,
  checkToken,
  getUserInfo,
  recharge,
  updateUserInfo,
  getUserProfile,
  applyBreeder,
  getCart,
  addToCart,
  removeFromCart,
  updateCartItem,
  getAvatarUploadUrl,
  confirmAvatarUpload,
  checkout,
  getMySheep,
  getMySheepUpdates,
  getOrderHistory,
  requestEndAdoption,
  payCareFee,
  getPromotionActivities,
  getAvailableCoupons,
  getUserCoupons,
  claimCoupon,
  followBreeder,
  getFollowedBreeders,
  getMonitorBreeders,
  getMonitorDevices,
  getHomeNews,
  getNewsDetail,
  getNewsList
}

Object.defineProperty(api, 'API_BASE_URL', {
  enumerable: true,
  get: getResolvedApiBaseUrl
})

module.exports = api

/**
 * 鍏虫敞/鍙栨秷鍏虫敞鍏绘畺鎴?
 * @param {string} token
 * @param {number} breederId
 * @param {boolean} follow
 */
function followBreeder(token, breederId, follow = true) {
  return request('/api/breeders/follow', 'POST', {
    token: token,
    breeder_id: breederId,
    follow: !!follow
  })
}

/**
 * 鑾峰彇鎴戠殑鍏虫敞鍏绘畺鎴峰垪琛?
 * @param {string} token
 */
function getFollowedBreeders(token) {
  return request('/api/breeders/follows?token=' + encodeURIComponent(token), 'GET')
}



