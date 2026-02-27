# 02 · 开发计划

## 总体阶段

| 阶段 | 名称 | 内容 | 状态 |
|------|------|------|------|
| Phase 1 | 基础搭建 | 项目结构、Docker、数据库迁移、种子数据 | ✅ 完成 |
| Phase 2 | 后端开发 | 所有 API 模块开发完成，Swagger 可调通 | ✅ 完成（42 routes） |
| Phase 3 | 前端开发 | C端 + B端所有页面实现 | ✅ 完成（31 pages，字段联调完毕） |
| Phase 4 | 联调收尾 | 全流程测试、Bug修复、文档完善 | ✅ 完成 |

## 快速入口

| 端 | 登录地址 | 账号 | 密码 |
|----|----------|------|------|
| C端用户 | http://localhost:5173/login | `13800000002` | `user123` |
| B端商户 | http://localhost:5173/merchant/login | `13900000001` | `merchant123` |
| 管理员 | http://localhost:5173/admin/login | `13800000000` | `admin123456` |
| API文档 | http://localhost:8000/docs | — | — |

---

## 详细任务拆解

### Phase 1 · 基础搭建

#### Step 1 · 项目脚手架
- [x] 创建 Monorepo 目录结构（`backend/` + `frontend/`）
- [x] 编写 `docker-compose.yml`（MySQL 8 + Redis 7）
- [x] 配置 `.env` 文件（DB连接、Redis连接、JWT Secret）
- [x] 创建 `backend/requirements.txt`
- [x] 初始化 `frontend/`（Vue 3 + Vite + Element Plus + Pinia + TypeScript）

**交付物**：`docker-compose up -d` 可启动 MySQL 和 Redis，后端框架可运行 ✅

---

#### Step 2 · 数据库设计与迁移
- [x] 编写所有建表 SQL（Alembic autogenerate — 13张表）
- [x] 配置 Alembic（`alembic init alembic`，配置 `env.py`）
- [x] 生成并执行初始迁移（`6a0428ce87c6_initial.py`）
- [x] 编写种子数据脚本 `backend/scripts/seed.py`：
  - 管理员账号：`13800000000 / admin123456`
  - 积分规则（注册送500积分、充值套餐）
  - 10个商品分类、1个审核通过商户、20+示例商品（含SKU）
  - 普通用户 `13800000002 / user123`（5000积分）
  - 3条商城公告、1个活动

**交付物**：`python scripts/seed.py` 执行9/9成功 ✅

---

### Phase 2 · 后端开发

#### Step 3 · 后端基础框架
- [x] `app/main.py`：FastAPI 实例、全局中间件（CORS）、路由注册
- [x] `app/core/config.py`：Pydantic Settings，读取 `.env`
- [x] `app/core/database.py`：SQLAlchemy Engine + Session + `get_db` 依赖
- [x] `app/core/redis.py`：Redis 客户端单例
- [x] `app/core/security.py`：JWT 签发/验证、密码哈希/验证
- [x] `app/core/exceptions.py`：自定义异常类 + 全局异常处理器
- [x] `app/core/response.py`：统一响应封装 `success()` / `paginated()`
- [x] `app/models/base.py`：Base Model 含 `id`、`created_at`、`updated_at`、`deleted_at` + 软删除 mixin

**交付物**：`GET /health` ✅，Swagger http://localhost:8000/docs ✅

---

#### Step 4-15 · 所有业务模块（一次性交付）

- [x] **认证**：注册/商户注册/登录/刷新/登出/短信/个人信息/改密码（`api/v1/auth.py`）
- [x] **用户**：地址CRUD（`api/v1/user.py`）
- [x] **积分**：余额查询/流水/话费流量快充（`api/v1/user.py` points endpoints）
- [x] **商品**：公开列表/详情/分类 + 商户CRUD/上下架（`api/v1/products.py`）
- [x] **购物车**：增删改查清（`api/v1/orders.py` cart部分）
- [x] **订单**：下单/列表/详情/取消/确认收货 + 商户发货（`api/v1/orders.py`）
- [x] **活动**：列表/详情 公开读（`api/v1/admin.py`）
- [x] **公告**：列表 公开读 + 管理员CRUD（`api/v1/admin.py`）
- [x] **管理员**：用户/商户/积分规则/订单/公告管理（`api/v1/admin.py`）
- [x] **商户B端**：dashboard + 商品管理 + 订单管理/发货（`api/v1/products.py` merchant部分）

**关键技术修复**（运行期间发现并修复）：
- bcrypt 直接使用，移除 passlib（Python 3.13 不兼容）
- 所有 status 字段为字符串：`"on_sale"/"pending"/"paid"/"shipped"` 等
- ORM 字段名以模型为准：`cover_image`、`min_points`、`total_sales`、`amount`（PointsRecord）

**交付物**：42 个路由全部可在 Swagger 调通 ✅

---

### Phase 3 · 前端开发

#### Step 16 · 前端基础架构
- [x] Vue Router 配置（三套路由 + 守卫）
- [x] Pinia Store（`useAuthStore`、`useCartStore`、`usePointsStore`）
- [x] Axios 封装（baseURL、Token 注入、401 自动刷新、统一错误提示）
- [x] 全局布局组件（C端 Layout、B端 Layout、Admin Layout）
- [x] 各页面与后端 API 联调（字段名全部对齐）

---

#### Step 17 · C端页面
- [x] 首页（Banner轮播 + 话费/流量快捷兑换 + 活动专区 + 商品列表Tab）
- [x] 商品列表页（左侧分类树 + 右侧商品网格 + 搜索/排序/筛选）
- [x] 商品详情页（主图 + SKU选择 + 立即兑换 + 加入购物车）
- [x] 购物车页（列表 + 结算合计）
- [x] 结算/下单页（地址 + 积分确认 + 提交）
- [x] 登录/注册页
- [x] 个人中心（积分 + 流水 + 模拟充值）
- [x] 我的订单（Tab分状态 + 操作按钮）
- [x] 我的地址（CRUD + 设为默认）
- [x] 公告列表/详情
- [x] 活动列表页
- [x] 搜索结果页
- [x] 404 页

---

#### Step 18 · 商户B端页面
- [x] 数据概览（关键指标卡片 + ECharts折线图）
- [x] 商品管理（Table + 新增/编辑弹框 + 上下架）
- [x] 库存管理（库存列表 + 低库存预警高亮）
- [x] 订单管理（筛选Tab + 发货弹框）
- [x] 数据分析（销量趋势 + 商品占比饼图）
- [x] 活动参与（浏览活动 + 申请参与）

---

#### Step 19 · 管理员B端页面
- [x] 系统概览（全平台指标）
- [x] 用户管理（搜索 + 封禁 + 调积分）
- [x] 商户管理（审核弹框：通过/拒绝+原因）
- [x] 积分规则配置（注册额度 + 充值套餐 CRUD）
- [x] 活动运营（创建活动 + 审核商户申请）
- [x] 报表分析（ECharts多图表）
- [x] 商城公告管理（CRUD + 置顶）
- [x] 系统维护（种子数据初始化按钮）

---

### Phase 4 · 联调收尾

#### Bug 修复记录（已完成）
- [x] `Inventory` 模型字段修正：`available_stock` → `quantity - locked_quantity`，`locked_stock` → `locked_quantity`
- [x] 订单/商户订单/管理员商户列表 `status` 参数类型修正：`Optional[int]` → `Optional[str]`
- [x] C端导航分类改为动态从 `/products/categories` 接口拉取，移除硬编码 slug
- [x] Banner 轮播改为真实背景图（Unsplash）+ 渐变蒙层，视觉更真实
- [x] 商户/管理员登录跳转修复：`router.push` 改 `router.replace`，加 `catch` 防静默失败
- [x] `admin_service.svc_admin_merchants` 过滤逻辑由 int 改为字符串直接比较

#### 待完成（全部已实现）
- [x] 全流程端对端测试
  - [x] C端：游客浏览 → 注册送积分 → 加购物车 → 下单 → 取消/确认收货
  - [x] B端商户：注册 → 管理员审核通过 → 上架商品 → 接单发货
  - [x] 管理员：审批商户 / 调整积分 / 封禁用户 / 发布公告
- [x] 商品评价功能接入
  - `review_service.py` 新增评价 service（防重复、状态校验）
  - `GET /products/{id}/reviews` 公开评价列表（含平均分、总数）
  - `POST /orders/{order_id}/items/{item_id}/review` 已完成订单写评价
  - 商品详情页展示评价列表 + 平均分 + 分页
  - 我的订单「已完成」状态新增"写评价"按钮 + 弹窗
- [x] 快速充值页（`/recharge`）话费流量充值后积分扣减逻辑验证
  - 流量套餐 `value` 修正为积分等价元数（与后端 `amount*100` 规则对齐）
  - 切换话费/流量 Tab 时自动重置已选金额
  - 充值成功展示消耗积分数
- [x] README.md 补全部署文档（含 Docker 一键启动、测试账号、功能模块说明）
- [x] 低库存预警通知
  - 商品 API 商户模式下携带 SKU 实际可用库存（`quantity - locked_quantity`）
  - 商户 Dashboard 顶部低库存预警横幅（stock < 10 时显示，点击跳转库存页）
  - 积分流水 `type` 字段补充 `phone_recharge` / `flow_recharge` 类型映射
