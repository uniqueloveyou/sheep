# 小程序后端接口文档

## 基础信息
- **基础URL**: `http://localhost:5000` 或生产环境地址
- **数据格式**: JSON
- **认证方式**: JWT Token（部分接口需要）

---

## 一、用户认证模块 (`/api/auth`)

### 1. 微信小程序登录
- **接口**: `POST /api/auth/login_wx` 或 `POST /login_wx`（兼容路径）
- **说明**: 微信小程序登录，自动注册新用户
- **请求参数**:
  ```json
  {
    "code": "微信wx.login()获取的code"
  }
  ```
- **返回格式**:
  ```json
  {
    "code": 0,  // 0:成功, 其他:错误
    "msg": "登录成功",
    "data": {
      "token": "jwt_token",
      "uid": 1,
      "openid": "openid_string",
      "mobile": "手机号(可选)"
    }
  }
  ```

### 2. 用户注册
- **接口**: `POST /api/auth/register`
- **说明**: 用户注册（可选，登录接口已支持自动注册）
- **请求参数**:
  ```json
  {
    "code": "微信code",
    "userInfo": {
      "nickName": "昵称",
      "avatarUrl": "头像URL",
      "gender": 0
    }
  }
  ```

### 3. 验证Token
- **接口**: `POST /api/auth/check_token` 或 `POST /check_token`（兼容路径）
- **说明**: 验证token有效性
- **请求参数**:
  ```json
  {
    "token": "jwt_token"
  }
  ```
  或 GET请求: `?token=jwt_token`
- **返回格式**:
  ```json
  {
    "code": 0,
    "msg": "token有效",
    "data": {
      "uid": 1,
      "openid": "openid_string"
    }
  }
  ```

### 4. 获取用户信息
- **接口**: `GET /api/auth/user_info`
- **说明**: 获取当前用户信息（需要token）
- **请求头**: `Authorization: Bearer {token}` 或参数 `?token=xxx`
- **返回格式**:
  ```json
  {
    "code": 0,
    "msg": "获取成功",
    "data": {
      "id": 1,
      "openid": "openid_string",
      "nickname": "昵称",
      "avatar_url": "头像URL",
      "mobile": "手机号"
    }
  }
  ```

### 5. 更新用户信息
- **接口**: `POST /api/auth/update_user_info`
- **说明**: 更新用户信息（需要token）
- **请求参数**:
  ```json
  {
    "token": "jwt_token",
    "userInfo": {
      "nickname": "新昵称",
      "avatar_url": "新头像",
      "mobile": "手机号"
    }
  }
  ```

---

## 二、羊只管理模块 (`/api/sheep`)

### 1. 搜索羊只
- **接口**: `GET /api/sheep/search` 或 `GET /search_sheep`（兼容路径）
- **说明**: 根据条件搜索羊只
- **请求参数**:
  - `gender`: 性别（如：公/母）
  - `weight`: 体重范围（格式：`min-max` 或 `min-max kg`）
  - `height`: 身高范围（格式：`min-max` 或 `min-max cm`）
  - `length`: 体长范围（格式：`min-max` 或 `min-max cm`）
- **示例**: `/api/sheep/search?gender=公&weight=40-50&height=60-70&length=80-100`
- **返回格式**: 羊只数组
  ```json
  [
    {
      "id": 1,
      "gender": "公",
      "weight": 45,
      "height": 65,
      "length": 90
    }
  ]
  ```

### 2. 根据ID获取羊只
- **接口**: `GET /api/sheep/{id}` 或 `GET /search_sheep_by_id?id={id}`（兼容路径）
- **说明**: 根据羊只ID获取详细信息
- **返回格式**:
  ```json
  {
    "id": 1,
    "gender": "公",
    "weight": 45,
    "height": 65,
    "length": 90
  }
  ```

### 3. 获取所有羊只（分页）
- **接口**: `GET /api/sheep`
- **说明**: 分页获取所有羊只列表
- **请求参数**:
  - `page`: 页码（默认：1）
  - `per_page`: 每页数量（默认：20，最大：100）
- **示例**: `/api/sheep?page=1&per_page=20`
- **返回格式**:
  ```json
  {
    "data": [...],
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  }
  ```

### 4. 商品搜索（通用）
- **接口**: `GET /search_goods`
- **说明**: 根据关键词搜索羊只（用于商品搜索功能）
- **请求参数**:
  - `keyword`: 搜索关键词
- **返回格式**:
  ```json
  [
    {
      "id": 1,
      "name": "羊只-公-45kg",
      "title": "羊只-公-45kg",
      "gender": "公",
      "weight": 45,
      "height": 65,
      "length": 90,
      "price": 300,
      "description": "羊只ID: 1, 性别: 公, 体重: 45kg...",
      "image": "/images/default.png"
    }
  ]
  ```

---

## 三、疫苗接种管理模块 (`/api/vaccine`)

### 1. 获取疫苗接种记录
- **接口**: `GET /api/vaccine/records/{sheep_id}`
- **说明**: 获取指定羊只的疫苗接种记录
- **返回格式**: 疫苗接种记录数组
  ```json
  [
    {
      "id": 1,
      "VaccinationID": "V001",
      "sheep_id": 1,
      "VaccinationDate": "2024-01-15",
      "ExpiryDate": "2024-07-15",
      "Dosage": "2ml",
      "AdministeredBy": "张医生",
      "VaccineType": "口蹄疫疫苗",
      "Notes": "备注信息"
    }
  ]
  ```

### 2. 添加疫苗接种记录
- **接口**: `POST /api/vaccine/records`
- **说明**: 添加新的疫苗接种记录
- **请求参数**:
  ```json
  {
    "VaccinationID": "V001",
    "sheep_id": 1,
    "VaccinationDate": "2024-01-15",
    "ExpiryDate": "2024-07-15",
    "Dosage": "2ml",
    "AdministeredBy": "张医生",
    "VaccineType": "口蹄疫疫苗",
    "Notes": "备注信息（可选）"
  }
  ```
- **返回格式**:
  ```json
  {
    "message": "Vaccination record added successfully",
    "status_code": 201
  }
  ```

### 3. 删除疫苗接种记录
- **接口**: `DELETE /api/vaccine/records/{record_id}`
- **说明**: 删除指定的疫苗接种记录
- **返回格式**:
  ```json
  {
    "message": "Vaccination record deleted successfully",
    "status_code": 200
  }
  ```

---

## 四、生长记录管理模块 (`/api/growth`)

### 1. 获取羊只完整数据
- **接口**: `GET /api/growth/sheep/{sheep_id}`
- **说明**: 获取羊只的完整数据（包括基本信息、生长记录、喂养记录）
- **返回格式**:
  ```json
  {
    "id": 1,
    "gender": "公",
    "current_weight": 45,
    "current_height": 65,
    "current_length": 90,
    "growth_records": [...],
    "feeding_records": [...]
  }
  ```

### 2. 获取生长记录
- **接口**: `GET /api/growth/records/{sheep_id}`
- **说明**: 获取指定羊只的生长记录
- **返回格式**: 生长记录数组

### 3. 获取喂养记录
- **接口**: `GET /api/growth/feeding/{sheep_id}`
- **说明**: 获取指定羊只的喂养记录
- **返回格式**: 喂养记录数组

---

## 五、养殖户管理模块 (`/api/breeders`)

### 1. 获取养殖户列表
- **接口**: `GET /api/breeders` 或 `GET /breeders`（兼容路径）
- **说明**: 获取所有养殖户信息（支持分页）
- **请求参数**:
  - `page`: 页码（默认：1）
  - `per_page`: 每页数量（默认：20，最大：100）
- **返回格式**:
  ```json
  {
    "data": [
      {
        "id": 1,
        "name": "张三",
        "gender": "男",
        "phone": "13800138000",
        "sheep_count": 50,
        "sheep_id": "S001",
        "female_count": 30,
        "male_count": 20,
        "iconUrl": "http://localhost:5001/images/farmer/people/p1.png"
      }
    ],
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  }
  ```

### 2. 获取单个养殖户信息
- **接口**: `GET /api/breeders/{id}` 或 `GET /breeders/{id}`（兼容路径）
- **说明**: 获取指定养殖户的详细信息
- **返回格式**: 养殖户对象

### 3. 添加养殖户
- **接口**: `POST /api/breeders`
- **说明**: 添加新的养殖户信息
- **请求参数**:
  ```json
  {
    "name": "张三",
    "gender": "男",
    "phone": "13800138000",
    "sheep_count": 50,
    "sheep_id": "S001",
    "female_count": 30,
    "male_count": 20
  }
  ```

### 4. 更新养殖户信息
- **接口**: `PUT /api/breeders/{id}`
- **说明**: 更新指定养殖户的信息
- **请求参数**: 同添加接口，字段可选

### 5. 删除养殖户
- **接口**: `DELETE /api/breeders/{id}`
- **说明**: 删除指定的养殖户信息

---

## 六、智能问答模块 (`/api/qa`)

### 1. 智能问答
- **接口**: `POST /api/qa/ask` 或 `POST /qa/ask`（兼容路径）
- **说明**: 调用大模型API进行智能问答（支持OpenAI、百度文心、阿里通义等）
- **请求参数**:
  ```json
  {
    "question": "滩羊的养殖方法"
  }
  ```
- **返回格式**:
  ```json
  {
    "answer": "滩羊养殖需要注意以下几点：\n1. 选择优质草场...",
    "status_code": 200
  }
  ```
- **说明**: 
  - 支持多种大模型（通过环境变量配置）
  - 如果大模型API不可用，会自动降级到本地回答
  - 本地回答基于关键词匹配，可回答常见问题

---

## 七、系统接口

### 1. 健康检查
- **接口**: `GET /health`
- **说明**: 检查服务是否正常运行
- **返回格式**:
  ```json
  {
    "status": "ok",
    "message": "Service is running"
  }
  ```

### 2. API首页
- **接口**: `GET /`
- **说明**: 显示API文档首页（HTML或JSON格式）

---

## 接口调用说明

### 1. 认证方式
- 需要token的接口，可以通过以下方式传递：
  - **请求头**: `Authorization: Bearer {token}`
  - **请求参数**: `?token={token}`
  - **POST body**: `{"token": "xxx"}`

### 2. 错误处理
- 所有接口统一返回格式：
  ```json
  {
    "error": "错误信息",
    "status_code": 400/401/404/500
  }
  ```
- 认证相关接口返回格式：
  ```json
  {
    "code": 错误码,
    "msg": "错误信息",
    "data": null
  }
  ```

### 3. 兼容性说明
- 后端提供了新旧两套API路径，确保小程序兼容性
- 建议使用新路径（`/api/xxx`），旧路径作为兼容保留

---

## 接口汇总表

| 模块 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 认证 | `/api/auth/login_wx` | POST | 微信登录 |
| 认证 | `/api/auth/check_token` | POST/GET | 验证token |
| 认证 | `/api/auth/user_info` | GET | 获取用户信息 |
| 认证 | `/api/auth/update_user_info` | POST | 更新用户信息 |
| 羊只 | `/api/sheep/search` | GET | 搜索羊只 |
| 羊只 | `/api/sheep/{id}` | GET | 获取羊只详情 |
| 羊只 | `/api/sheep` | GET | 获取羊只列表 |
| 羊只 | `/search_goods` | GET | 商品搜索 |
| 疫苗 | `/api/vaccine/records/{sheep_id}` | GET | 获取疫苗记录 |
| 疫苗 | `/api/vaccine/records` | POST | 添加疫苗记录 |
| 疫苗 | `/api/vaccine/records/{id}` | DELETE | 删除疫苗记录 |
| 生长 | `/api/growth/sheep/{sheep_id}` | GET | 获取羊只完整数据 |
| 生长 | `/api/growth/records/{sheep_id}` | GET | 获取生长记录 |
| 生长 | `/api/growth/feeding/{sheep_id}` | GET | 获取喂养记录 |
| 养殖户 | `/api/breeders` | GET | 获取养殖户列表 |
| 养殖户 | `/api/breeders/{id}` | GET | 获取养殖户详情 |
| 养殖户 | `/api/breeders` | POST | 添加养殖户 |
| 养殖户 | `/api/breeders/{id}` | PUT | 更新养殖户 |
| 养殖户 | `/api/breeders/{id}` | DELETE | 删除养殖户 |
| 问答 | `/api/qa/ask` | POST | 智能问答 |
| 系统 | `/health` | GET | 健康检查 |

