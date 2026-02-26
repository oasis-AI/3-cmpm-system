# 05 · API 规范

## 1. 统一响应格式

### 成功响应
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

### 分页响应（data 结构）
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 错误响应
```json
{
  "code": 40001,
  "message": "积分余额不足",
  "data": null
}
```

---

## 2. 错误码

| code | 说明 |
|------|------|
| 0 | 成功 |
| 40001 | 参数错误 |
| 40100 | 未登录 / Token 无效 |
| 40101 | Token 已过期 |
| 40102 | Token 已注销（黑名单） |
| 40300 | 权限不足 |
| 40301 | 商户未审核通过 |
| 40400 | 资源不存在 |
| 40900 | 资源冲突（如手机号已注册） |
| 42200 | 积分余额不足 |
| 42201 | 库存不足 |
| 42202 | 活动已结束或额满 |
| 50000 | 服务器内部错误 |

---

## 3. 认证规范

### Header
```
Authorization: Bearer <access_token>
```

### Token 刷新
- `access_token` 有效期：**120分钟**
- `refresh_token` 有效期：**7天**
- 前端 Axios 拦截器：收到 HTTP 401 后，自动调 `/api/v1/auth/refresh` 刷新，再重试原请求

### 路由权限说明
- **公开接口**（无需 Token）：商品列表/详情、公告列表、话费流量套餐查询
- **用户接口**（需 role=user 或任意已登录）：购物车、下单、个人信息、积分
- **商户接口**（需 role=merchant + status=approved）：商品/库存/订单管理
- **管理员接口**（需 role=admin）：所有管理后台接口

---

## 4. 路由前缀约定

| 路由前缀 | 说明 | 权限 |
|----------|------|------|
| `GET /api/v1/public/*` | 公开接口 | 无需 Token |
| `POST /api/v1/auth/*` | 认证接口 | 特殊处理 |
| `/api/v1/user/*` | 用户个人接口 | 需登录 |
| `/api/v1/merchant/*` | 商户B端接口 | 需商户权限 |
| `/api/v1/admin/*` | 管理员接口 | 需管理员权限 |

---

## 5. 全接口列表

### Auth（认证）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| POST | `/api/v1/auth/register` | 公开 | 注册（自动赠送积分） |
| POST | `/api/v1/auth/login` | 公开 | 登录 |
| POST | `/api/v1/auth/refresh` | 公开（需 refresh_token） | 刷新 access_token |
| POST | `/api/v1/auth/logout` | 需登录 | 登出（写黑名单） |
| POST | `/api/v1/auth/merchant/register` | 公开 | 商户注册申请 |

### Users（用户）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| GET | `/api/v1/user/profile` | 用户 | 获取个人信息 |
| PUT | `/api/v1/user/profile` | 用户 | 修改昵称/头像 |
| PUT | `/api/v1/user/password` | 用户 | 修改密码 |
| GET | `/api/v1/user/addresses` | 用户 | 收货地址列表 |
| POST | `/api/v1/user/addresses` | 用户 | 新增地址 |
| PUT | `/api/v1/user/addresses/{id}` | 用户 | 修改地址 |
| DELETE | `/api/v1/user/addresses/{id}` | 用户 | 软删除地址 |

### Points（积分）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| GET | `/api/v1/user/points/balance` | 用户 | 查询积分余额 |
| GET | `/api/v1/user/points/records` | 用户 | 积分流水（分页） |
| GET | `/api/v1/public/points/recharge-packages` | 公开 | 充值套餐列表 |
| POST | `/api/v1/user/points/recharge` | 用户 | 模拟充值（选套餐） |

### Categories（分类）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| GET | `/api/v1/public/categories` | 公开 | 分类树（含二级） |

### Products（商品）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| GET | `/api/v1/public/products` | 公开 | 商品列表（分页+筛选+排序） |
| GET | `/api/v1/public/products/{id}` | 公开 | 商品详情（含SKU、图片、评价） |
| GET | `/api/v1/public/products/search` | 公开 | 关键词搜索 |
| POST | `/api/v1/merchant/products` | 商户 | 新增商品 |
| PUT | `/api/v1/merchant/products/{id}` | 商户 | 编辑商品 |
| DELETE | `/api/v1/merchant/products/{id}` | 商户 | 软删除商品 |
| PUT | `/api/v1/merchant/products/{id}/status` | 商户 | 上架/下架 |
| GET | `/api/v1/merchant/products` | 商户 | 商户自己的商品列表 |

### Inventory（库存）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| GET | `/api/v1/merchant/inventory` | 商户 | 库存列表（含低库存标注） |
| PUT | `/api/v1/merchant/inventory/{sku_id}` | 商户 | 调整库存数量 |

### Cart（购物车）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| GET | `/api/v1/user/cart` | 用户 | 购物车列表 |
| POST | `/api/v1/user/cart` | 用户 | 加入购物车 |
| PUT | `/api/v1/user/cart/{id}` | 用户 | 修改数量 |
| DELETE | `/api/v1/user/cart/{id}` | 用户 | 删除单项 |
| DELETE | `/api/v1/user/cart/selected` | 用户 | 删除指定多项 |

### Orders（订单）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| POST | `/api/v1/user/orders` | 用户 | 提交订单（积分扣减+库存预占） |
| GET | `/api/v1/user/orders` | 用户 | 我的订单（分页+状态筛选） |
| GET | `/api/v1/user/orders/{order_no}` | 用户 | 订单详情 |
| PUT | `/api/v1/user/orders/{order_no}/confirm` | 用户 | 确认收货 |
| POST | `/api/v1/user/orders/{order_no}/refund` | 用户 | 申请售后/退款 |
| GET | `/api/v1/merchant/orders` | 商户 | 商户订单列表 |
| PUT | `/api/v1/merchant/orders/{order_no}/ship` | 商户 | 发货（填快递信息） |
| PUT | `/api/v1/merchant/orders/{order_no}/refund` | 商户 | 处理退款申请（通过/拒绝） |

### Reviews（评价）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| POST | `/api/v1/user/reviews` | 用户 | 提交评价（确认收货后） |
| GET | `/api/v1/public/products/{id}/reviews` | 公开 | 商品评价列表 |

### Quick Recharge（快捷兑换）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| GET | `/api/v1/public/quick-recharge/packages` | 公开 | 话费/流量套餐列表 |
| POST | `/api/v1/user/quick-recharge/phone` | 用户 | 话费充值（扣积分） |
| POST | `/api/v1/user/quick-recharge/flow` | 用户 | 流量充值（扣积分） |
| GET | `/api/v1/user/quick-recharge/records` | 用户 | 充值记录 |

### Activities（活动）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| GET | `/api/v1/public/activities` | 公开 | 活动列表（进行中） |
| GET | `/api/v1/public/activities/{id}` | 公开 | 活动详情（含商品） |
| POST | `/api/v1/user/activities/{id}/join` | 用户 | 参与活动（报名限额） |
| POST | `/api/v1/merchant/activities/{id}/apply` | 商户 | 商品参与活动申请 |
| POST | `/api/v1/admin/activities` | 管理员 | 创建活动 |
| PUT | `/api/v1/admin/activities/{id}` | 管理员 | 编辑活动 |
| PUT | `/api/v1/admin/activities/{id}/products/{pid}` | 管理员 | 审核商户申请 |

### Announcements（公告）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| GET | `/api/v1/public/announcements` | 公开 | 公告列表（置顶在前） |
| GET | `/api/v1/public/announcements/{id}` | 公开 | 公告详情 |
| POST | `/api/v1/admin/announcements` | 管理员 | 发布公告 |
| PUT | `/api/v1/admin/announcements/{id}` | 管理员 | 编辑公告 |
| DELETE | `/api/v1/admin/announcements/{id}` | 管理员 | 软删除公告 |

### Admin（管理员）
| Method | Path | 权限 | 说明 |
|--------|------|------|------|
| GET | `/api/v1/admin/users` | 管理员 | 用户列表（搜索+分页） |
| PUT | `/api/v1/admin/users/{id}/ban` | 管理员 | 封禁/解封用户 |
| POST | `/api/v1/admin/users/{id}/points` | 管理员 | 手动增减积分 |
| GET | `/api/v1/admin/merchants` | 管理员 | 商户列表（含pending） |
| PUT | `/api/v1/admin/merchants/{id}/review` | 管理员 | 审核商户 |
| GET | `/api/v1/admin/points-rules` | 管理员 | 积分规则列表 |
| POST | `/api/v1/admin/points-rules` | 管理员 | 新增规则 |
| PUT | `/api/v1/admin/points-rules/{id}` | 管理员 | 编辑规则 |
| DELETE | `/api/v1/admin/points-rules/{id}` | 管理员 | 删除规则 |
| GET | `/api/v1/admin/reports/overview` | 管理员 | 全平台概览数据 |
| GET | `/api/v1/admin/reports/points-trend` | 管理员 | 积分发放/消耗趋势 |
| GET | `/api/v1/admin/reports/sales-rank` | 管理员 | 商户销售排行 |

---

## 6. 请求/响应示例

### 注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "phone": "13800138000",
  "password": "password123",
  "nickname": "测试用户"
}
```
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "phone": "138****8000",
      "nickname": "测试用户",
      "role": "user",
      "points_balance": 1000
    }
  }
}
```

### 商品列表查询参数
```
GET /api/v1/public/products?category_id=1&page=1&page_size=20&sort=min_points_asc&keyword=纸巾&tag=精选
```
