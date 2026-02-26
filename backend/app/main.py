from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import BusinessException, business_exception_handler, global_exception_handler

app = FastAPI(
    title=settings.APP_TITLE,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


@app.get("/health", tags=["Health"])
def health_check():
    from app.core.redis import check_redis_connection
    return {
        "status": "ok",
        "app": settings.APP_TITLE,
        "redis": "ok" if check_redis_connection() else "error",
    }


# ---------- 注册路由 ----------
from app.api.v1 import auth, products, orders, user, admin

app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
