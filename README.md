# 中国移动积分商城系统

> 全栈 Demo 项目，对标 jf.10086.cn，功能完整、前后端分离。

---

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | FastAPI · SQLAlchemy 2.x · Alembic · PyMySQL · bcrypt · PyJWT |
| 前端 | Vue 3 · Vite · Element Plus · Pinia · Vue Router · TypeScript |
| 基础设施 | MySQL 8 · Redis 7 · Docker Compose |
| Python | 3.13（venv 在 `.venv/`） |

---

## 快速启动

### 前置要求

- Docker + Docker Compose
- Python 3.13
- Node.js 18+

### 1. 克隆并配置环境变量

```bash
git clone <repo-url>
cd 3-cmpm-system

# 复制并编辑环境变量（根目录 .env）
cp .env.example .env
# 按需修改 .env 中的数据库密码、JWT Secret 等
```

`.env` 关键字段：

```env
DATABASE_URL=mysql+pymysql://root:rootpassword@127.0.0.1:3306/cmpm_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key-change-this
ADMIN_PHONE=13800000000
ADMIN_PASSWORD=admin123456
```

### 2. 启动 MySQL + Redis

```bash
docker-compose up -d
# 等待健康检查通过（约 10 秒）
docker-compose ps
```

### 3. 初始化后端

```bash
cd backend

# 创建并激活 Python 虚拟环境（首次）
python3.13 -m venv ../.venv
source ../.venv/bin/activate   # Windows: ..\.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 执行数据库迁移
alembic upgrade head

# 初始化种子数据（管理员、商户、用户、商品、分类等）
python scripts/seed.py

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端启动成功后：
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

---

## 测试账号

| 角色 | 手机号 | 密码 | 积分余额 |
|------|--------|------|---------|
| 管理员 | `13800000000` | `admin123456` | — |
| 商户 | `13900000001` | `merchant123` | — |
| 普通用户 | `13800000002` | `user123` | 5000 |

---

## 访问地址

| 服务 | 地址 |
|------|------|
| C 端首页 | http://localhost:5173 |
| B 端商户后台 | http://localhost:5173/merchant/login |
| 管理员后台 | http://localhost:5173/admin/login |
| API 文档 (Swagger) | http://localhost:8000/docs |

---

## 项目结构

```
.
├── .env                    # 环境变量（不提交到 Git）
├── docker-compose.yml      # MySQL + Redis
├── backend/
│   ├── app/
│   │   ├── api/v1/         # 路由层（auth, products, orders, user, admin）
│   │   ├── core/           # config, database, deps, exceptions, security, response
│   │   ├── models/         # SQLAlchemy ORM 模型（13 张表）
│   │   ├── schemas/        # Pydantic v2 请求/响应模型
│   │   └── services/       # 业务逻辑层
│   ├── alembic/            # 数据库迁移
│   └── scripts/seed.py     # 种子数据
└── frontend/
    └── src/
        ├── api/            # Axios 请求模块（按域划分）
        ├── stores/         # Pinia 状态（auth, cart, points）
        ├── views/          # 页面（c/ · merchant/ · admin/）
        └── layouts/        # 三套布局组件
```

---

## 功能模块

### C 端（用户）
- 游客：浏览商品 / 搜索 / 查看公告活动
- 注册/登录（密码登录，注册赠 500 积分）
- 购物车 → 结算 → 下单（积分即时扣除）
- 我的订单（取消 / 确认收货 / 写评价）
- 我的积分（余额 + 流水明细）
- 话费/流量充值（积分兑换，Mock）
- 我的地址（CRUD + 设为默认）

### B 端商户
- 注册 → 管理员审核 → 上架商品
- 商品管理（CRUD + 上下架 + SKU）
- 库存管理（库存预警高亮）
- 订单管理（筛选 + 发货）
- 数据概览 / 数据分析

### 管理员
- 用户管理（搜索 + 封禁 + 调积分）
- 商户审核（通过 / 拒绝 + 原因）
- 积分规则（注册赠送 + 充值套餐 CRUD）
- 活动运营（创建 + 审核商户申请）
- 公告管理（CRUD + 置顶）
- 报表分析

---

## 生产部署（Docker 全栈）

```bash
# 构建并启动所有服务
docker-compose -f docker-compose.prod.yml up -d --build
```

> 生产 compose 文件需根据实际域名配置 Nginx 反代。后端 Dockerfile 和前端 Dockerfile + nginx.conf 已就绪，可直接用于容器化部署。

---

## 开发规范

详见 [docs/08-dev-standards.md](docs/08-dev-standards.md)

- 所有接口使用 `success()` / `paginated()` 统一响应
- 业务错误使用 `BusinessException(ErrCode.XXX)`，禁用 `HTTPException`
- 所有模型含 `deleted_at` 软删除，查询必须加 `.filter(Model.deleted_at.is_(None))`
- ORM 禁用 `relationship()`，手动 join 查询
- Status 字段全为字符串：`"on_sale"` / `"pending"` / `"paid"` / `"shipped"`

---

## 文档

| 文档 | 内容 |
|------|------|
| [docs/01-project-overview.md](docs/01-project-overview.md) | 项目总览 |
| [docs/02-dev-plan.md](docs/02-dev-plan.md) | 开发计划与进度 |
| [docs/03-architecture.md](docs/03-architecture.md) | 系统架构 |
| [docs/04-database.md](docs/04-database.md) | 数据库设计 |
| [docs/05-api-spec.md](docs/05-api-spec.md) | API 规范 |
| [docs/09-points-system.md](docs/09-points-system.md) | 积分系统设计 |
