# 03 · 系统架构

## 1. Monorepo 目录结构

```
cmpm-system/
├── docs/                          # 项目文档
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI 入口，注册路由、中间件
│   │   ├── core/
│   │   │   ├── config.py          # Pydantic Settings，读取 .env
│   │   │   ├── database.py        # SQLAlchemy Engine + Session
│   │   │   ├── redis.py           # Redis 客户端单例
│   │   │   ├── security.py        # JWT 工具、密码哈希
│   │   │   ├── deps.py            # FastAPI Depends：认证、权限
│   │   │   ├── exceptions.py      # 自定义异常 + 全局处理器
│   │   │   └── response.py        # 统一响应封装
│   │   ├── models/                # SQLAlchemy Table 定义（无 relationship）
│   │   │   ├── base.py            # Base + 软删除 Mixin
│   │   │   ├── user.py
│   │   │   ├── merchant.py
│   │   │   ├── product.py         # categories + products + skus + images
│   │   │   ├── inventory.py
│   │   │   ├── cart.py
│   │   │   ├── order.py           # orders + order_items
│   │   │   ├── points.py          # points_rules + points_records
│   │   │   ├── review.py
│   │   │   ├── activity.py        # activities + products + participants
│   │   │   ├── announcement.py
│   │   │   └── quick_recharge.py
│   │   ├── schemas/               # Pydantic Request/Response 模型
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   ├── points.py
│   │   │   └── ...
│   │   ├── services/              # 业务逻辑层（所有跨表操作在此）
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── product_service.py
│   │   │   ├── inventory_service.py
│   │   │   ├── cart_service.py
│   │   │   ├── order_service.py
│   │   │   ├── points_service.py
│   │   │   ├── review_service.py
│   │   │   ├── activity_service.py
│   │   │   ├── quick_recharge_service.py
│   │   │   ├── announcement_service.py
│   │   │   └── admin_service.py
│   │   └── api/
│   │       └── v1/
│   │           ├── __init__.py    # 注册所有路由
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── products.py
│   │           ├── inventory.py
│   │           ├── cart.py
│   │           ├── orders.py
│   │           ├── points.py
│   │           ├── reviews.py
│   │           ├── activities.py
│   │           ├── quick_recharge.py
│   │           ├── announcements.py
│   │           └── admin.py
│   ├── alembic/                   # 数据库迁移
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── scripts/
│   │   └── seed.py                # 种子数据初始化脚本
│   ├── tests/                     # 单元/集成测试（可选）
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env                       # 不进 Git
├── frontend/
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── assets/
│   │   │   └── styles/
│   │   │       ├── variables.scss  # 主色变量
│   │   │       └── global.scss
│   │   ├── components/             # 公共组件
│   │   │   ├── common/             # 通用：SearchBar、ProductCard、Pagination
│   │   │   ├── c/                  # C端专用组件
│   │   │   └── b/                  # B端专用组件（统计卡片、图表等）
│   │   ├── layouts/
│   │   │   ├── CLayout.vue         # C端主布局（Header + Footer）
│   │   │   ├── MerchantLayout.vue  # 商户后台布局（侧边菜单）
│   │   │   └── AdminLayout.vue     # 管理员后台布局
│   │   ├── views/
│   │   │   ├── c/                  # C端页面
│   │   │   │   ├── Home.vue
│   │   │   │   ├── ProductList.vue
│   │   │   │   ├── ProductDetail.vue
│   │   │   │   ├── Cart.vue
│   │   │   │   ├── Checkout.vue
│   │   │   │   ├── Login.vue
│   │   │   │   ├── Register.vue
│   │   │   │   ├── user/
│   │   │   │   │   ├── Profile.vue
│   │   │   │   │   ├── Points.vue
│   │   │   │   │   ├── Orders.vue
│   │   │   │   │   └── Address.vue
│   │   │   │   └── announcements/
│   │   │   ├── merchant/           # 商户B端页面
│   │   │   │   ├── Dashboard.vue
│   │   │   │   ├── Products.vue
│   │   │   │   ├── Inventory.vue
│   │   │   │   ├── Orders.vue
│   │   │   │   ├── Analytics.vue
│   │   │   │   └── Activities.vue
│   │   │   └── admin/              # 管理员B端页面
│   │   │       ├── Dashboard.vue
│   │   │       ├── Users.vue
│   │   │       ├── Merchants.vue
│   │   │       ├── PointsRules.vue
│   │   │       ├── Activities.vue
│   │   │       ├── Reports.vue
│   │   │       ├── Announcements.vue
│   │   │       └── System.vue
│   │   ├── router/
│   │   │   ├── index.ts
│   │   │   ├── c.routes.ts
│   │   │   ├── merchant.routes.ts
│   │   │   └── admin.routes.ts
│   │   ├── stores/
│   │   │   ├── auth.ts             # 用户认证状态（token、userInfo、role）
│   │   │   ├── cart.ts             # 购物车
│   │   │   └── points.ts           # 积分余额缓存
│   │   └── api/
│   │       ├── request.ts          # Axios 实例 + 拦截器
│   │       ├── auth.ts
│   │       ├── products.ts
│   │       ├── orders.ts
│   │       ├── points.ts
│   │       └── ...
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## 2. 后端分层架构

```
HTTP Request
    │
    ▼
┌─────────────────────────────────┐
│  Router Layer (api/v1/*.py)     │  参数解析、权限Depends、调用Service
└─────────────────┬───────────────┘
                  │
                  ▼
┌─────────────────────────────────┐
│  Service Layer (services/*.py)  │  所有业务逻辑、跨表操作、事务控制
└──────────┬──────────┬───────────┘
           │          │
           ▼          ▼
┌──────────────┐  ┌──────────────┐
│  Model Layer │  │  Redis Layer │
│ (models/*.py)│  │ (core/redis) │
└──────┬───────┘  └──────────────┘
       │
       ▼
┌──────────────┐
│   MySQL DB   │
└──────────────┘
```

---

## 3. 前端路由架构

```
/ (CLayout)
├── /                        → Home.vue（游客可访问）
├── /products                → ProductList.vue
├── /product/:id             → ProductDetail.vue
├── /cart                    → Cart.vue（需登录）
├── /checkout                → Checkout.vue（需登录）
├── /login                   → Login.vue
├── /register                → Register.vue
├── /announcements           → 公告列表
├── /user（需登录）
│   ├── /user/profile        → 个人信息
│   ├── /user/points         → 积分管理
│   ├── /user/orders         → 我的订单
│   └── /user/address        → 收货地址

/merchant（需 role=merchant + status=approved）
├── /merchant/dashboard      → 数据概览
├── /merchant/products       → 商品管理
├── /merchant/inventory      → 库存管理
├── /merchant/orders         → 订单管理
├── /merchant/analytics      → 数据分析
└── /merchant/activities     → 活动参与

/admin（需 role=admin）
├── /admin/dashboard         → 系统概览
├── /admin/users             → 用户管理
├── /admin/merchants         → 商户管理
├── /admin/points-rules      → 积分规则
├── /admin/activities        → 活动运营
├── /admin/reports           → 报表分析
├── /admin/announcements     → 公告管理
└── /admin/system            → 系统维护
```

---

## 4. Redis 使用场景

| 场景 | Key 设计 | 数据结构 | TTL |
|------|----------|----------|-----|
| JWT 黑名单（登出失效） | `token:blacklist:{jti}` | String | 至 Token 过期时间 |
| 库存预占（防超卖） | `inventory:stock:{sku_id}` | String（数字） | 永久（与DB同步） |
| 活动报名限额 | `activity:quota:{activity_id}` | String（数字） | 至活动结束 |
| 积分操作分布式锁 | `lock:points:{user_id}` | String | 5s |

---

## 5. Docker Compose 服务

```yaml
services:
  mysql:
    image: mysql:8.0
    ports: ["3306:3306"]
    environment:
      MYSQL_DATABASE: cmpm_db
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [mysql, redis]
    env_file: .env

  frontend:
    build: ./frontend
    ports: ["5173:80"]
    depends_on: [backend]
```

---

## 6. 环境变量（.env.example）

```env
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=cmpm_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=120
JWT_REFRESH_EXPIRE_DAYS=7

# App
DEBUG=true
```
