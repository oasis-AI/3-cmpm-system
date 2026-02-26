# 中国移动积分商城系统 - 文档导航

> Demo 项目，功能完整，对标真实 jf.10086.cn

## 文档列表

| 文档 | 说明 |
|------|------|
| [01-project-overview.md](./01-project-overview.md) | 项目总览：背景、角色、技术选型、核心约束 |
| [02-dev-plan.md](./02-dev-plan.md) | 开发计划：阶段划分、里程碑、任务清单 |
| [03-architecture.md](./03-architecture.md) | 系统架构：目录结构、分层设计、部署方案 |
| [04-database.md](./04-database.md) | 数据库设计：所有表结构、字段说明、关联关系 |
| [05-api-spec.md](./05-api-spec.md) | API 规范：响应格式、错误码、接口列表 |
| [06-frontend-c.md](./06-frontend-c.md) | C 端设计：页面清单、UI 规范、路由、交互流程 |
| [07-frontend-b.md](./07-frontend-b.md) | B 端设计：商户端 + 管理员端、权限矩阵 |
| [08-dev-standards.md](./08-dev-standards.md) | 开发规范：命名、Git、软删除、代码风格 |
| [09-points-system.md](./09-points-system.md) | 积分系统：规则、流转、防超卖方案 |

## 快速启动

```bash
# 1. 启动 MySQL + Redis
docker-compose up -d

# 2. 后端（Python 3.13 venv 在项目根目录）
cd backend
source ../.venv/bin/activate
alembic upgrade head          # 初次运行才需要
python scripts/seed.py        # 初次运行才需要
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. 前端
cd frontend && npm run dev    # http://localhost:5173
```

> **注意**：`.env` 在项目根目录，不要编辑 `backend/.env`（不存在）。

## 测试账号（种子数据）

| 角色 | 手机号 | 密码 |
|------|--------|------|
| 管理员 | 13800000000 | admin123456 |
| 商户 | 13900000001 | merchant123 |
| 普通用户 | 13800000002 | user123（5000积分） |

## 访问地址

| 服务 | 地址 |
|------|------|
| C 端前端 | http://localhost:5173 |
| B 端前端（商户/管理员共用路由区分） | http://localhost:5173/merchant、/admin |
| 后端 API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Redoc | http://localhost:8000/redoc |
