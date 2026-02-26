# 01 · 项目总览

## 1. 项目背景

本项目是对标 **中国移动积分商城**（jf.10086.cn）的 Demo 实现。  
目标：功能完整、UI 真实感强，供全栈开发学习与演示使用，不涉及真实支付和运营。

> 真实站点已将"积分"更名为"AI豆"，本 Demo 统一沿用 **"积分"** 表述。

---

## 2. 三类角色

| 角色 | 说明 | 登录要求 |
|------|------|----------|
| **游客** | 可浏览商品、查看活动，无法兑换 | 无需登录 |
| **用户（C端）** | 注册用户，可兑换商品、查看订单、管理积分 | 需登录 |
| **商户（B端）** | 入驻商家，管理商品、库存、订单，需审核通过 | 需登录 + 审核通过 |
| **管理员（B端）** | 平台运营方，审核商户、配置积分规则、运营活动 | 需登录 + admin 角色 |

---

## 3. 技术选型

### 后端
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 运行环境 |
| FastAPI | 0.115+ | Web 框架，自带 Swagger UI |
| SQLAlchemy | 2.x | ORM（仅 Core 风格，不使用 relationship） |
| Alembic | latest | 数据库迁移 |
| MySQL | 8.0 | 主数据库 |
| Redis | 7.x | JWT 黑名单、库存预占、活动限额 |
| PyJWT | 2.x | JWT 签发与验证 |
| Passlib + bcrypt | latest | 密码哈希 |
| python-dotenv | latest | 环境变量管理 |

### 前端
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.x | 前端框架 |
| Vite | 5.x | 构建工具 |
| Vue Router | 4.x | 路由管理（含三套路由守卫） |
| Pinia | 2.x | 状态管理 |
| Element Plus | 2.x | UI 组件库 |
| ECharts | 5.x | 数据分析图表 |
| Axios | 1.x | HTTP 请求（含拦截器、Token 刷新） |

### 基础设施
| 技术 | 用途 |
|------|------|
| Docker + Docker Compose | 本地一键启动所有服务 |

---

## 4. 核心约束（必须遵守）

### 4.1 软删除
- **所有表**均含 `deleted_at DATETIME NULL` 字段
- 删除操作：`UPDATE table SET deleted_at = NOW() WHERE id = ?`（禁止物理删除）
- 所有查询默认加条件：`WHERE deleted_at IS NULL`
- Service 层封装统一的软删除方法，禁止在 router 层直接操作

### 4.2 禁用 SQLAlchemy relationship
- 不使用 `relationship()`、`backref`、`lazy loading`
- 所有跨表关联通过 Service 层 **手动 JOIN** 或 **二次查询** 实现
- 目的：逻辑清晰、避免 N+1 问题隐患、方便后续分库分表

### 4.3 统一 API 响应格式
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```
详见 [05-api-spec.md](./05-api-spec.md)

### 4.4 分层架构（后端）
```
Router → Service → Model（Query）→ DB/Redis
```
- Router：只负责参数解析、权限 Depends、调用 Service
- Service：所有业务逻辑，禁止在 Router 写业务
- Model：定义表结构，提供静态查询方法

---

## 5. 积分说明

- 单位：**积分**（整数，最小粒度 1）
- 来源：注册赠送、模拟充值
- 消耗：兑换商品、话费兑换、流量兑换
- 退回：售后申请通过后积分返还
- 有效期：Demo 中不设过期机制

---

## 6. 主色调

| 名称 | 色值 | 用途 |
|------|------|------|
| 中国移动绿 | `#00A854` | 主色、按钮、导航 |
| 积分橙 | `#FF6600` | 积分数字、价格、促销标签 |
| 背景灰 | `#F5F5F5` | 页面底色 |
| 白色 | `#FFFFFF` | 卡片、弹框 |
| 文字主色 | `#333333` | 正文 |
| 文字次色 | `#999999` | 辅助说明 |
