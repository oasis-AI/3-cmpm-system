# 中国移动积分商城 — Copilot Instructions

## Project Overview

Demo full-stack e-commerce points mall (对标 jf.10086.cn). Three roles: C端用户、B端商户、管理员. See `docs/` for detailed specs.

**Test accounts:** admin `13800000000/admin123456` · merchant `13900000001/merchant123` · user `13800000002/user123`

## Architecture

```
.
├── backend/          # FastAPI + SQLAlchemy 2.x + Alembic + PyMySQL
│   ├── app/
│   │   ├── api/v1/   # Routers (auth, products, orders, user, admin)
│   │   ├── core/     # config, database, deps, exceptions, redis, response, security
│   │   ├── models/   # SQLAlchemy ORM models (no relationship(), use manual joins)
│   │   ├── schemas/  # Pydantic v2 request/response models
│   │   └── services/ # Business logic layer (auth_service, product_service, …)
│   ├── alembic/      # DB migrations
│   └── scripts/seed.py
├── frontend/         # Vue 3 + Vite + Element Plus + Pinia + Vue Router
│   └── src/
│       ├── api/      # Axios modules per domain; request.ts handles token refresh
│       ├── stores/   # Pinia (auth.ts, cart.ts, points.ts)
│       ├── views/    # Pages organized by role (c/, b/, admin/)
│       └── layouts/  # Layout components wrapping views
```

## Backend Conventions

- **Always** use `from app.core.response import success, paginated` for all router responses — never return raw dicts.
- **Business errors:** raise `BusinessException(ErrCode.XXX, "message")` from `app.core.exceptions`. Do not use `HTTPException`.
- **Auth guards** in `app.core.deps`: `get_current_user`, `require_merchant`, `require_admin` — inject via `Depends()`.
- **No `relationship()`** in models — always query explicitly. Example: `db.query(Category).filter(Category.id == product.category_id).first()`.
- **Soft deletes:** all models have `deleted_at`; filters must include `.filter(Model.deleted_at.is_(None))`.
- **Status fields are strings**, not ints:
  - `Product.status`: `"on_sale"` / `"off_shelf"` / `"pending"`
  - `Order.status`: `"pending"` / `"paid"` / `"shipped"` / `"completed"` / `"cancelled"`
  - `Merchant.status`: `"pending"` / `"approved"` / `"rejected"`
- **PointsRecord fields:** `amount` (int, positive=credit), `type` (string e.g. `"register"`, `"exchange"`, `"refund"`), `balance_after`.
- **bcrypt** used directly (`import bcrypt`) — passlib is removed (incompatible with Python 3.13).
- Python venv: `/Users/shiyu/liulin/1-project/3-cmpm-system/.venv` (Python 3.13)

## Frontend Conventions

- All API calls go through `src/api/request.ts` (axios instance with `/api/v1` baseURL + auto token injection + 401 refresh logic).
- Add new API modules in `src/api/<domain>.ts` following existing files like `src/api/products.ts`.
- State: Pinia stores in `src/stores/`. Auth state (`token`, `refreshToken`, `user`) persisted via `localStorage`.
- Vite proxy forwards `/api` → `http://localhost:8000`.

## Build & Run

```bash
# Infrastructure (MySQL + Redis)
docker-compose up -d

# Backend
cd backend
source ../.venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# DB migrations (run from backend/)
alembic upgrade head

# Seed data
python scripts/seed.py

# Frontend
cd frontend
npm run dev        # http://localhost:5173
npm run build
```

## Integration

- **DB:** `root:rootpassword@127.0.0.1:3306/cmpm_db` (set in root `.env`)
- **Redis:** `localhost:6379` (token blacklist, SMS codes)
- **Auth:** JWT — `create_access_token` / `create_refresh_token` / `decode_token` in `app.core.security`
- **Env:** `backend/app/core/config.py` reads from `("../.env", ".env")` — edit root `.env`, not `backend/.env`
- **API docs:** http://localhost:8000/docs
