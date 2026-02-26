from fastapi import Request
from fastapi.responses import JSONResponse


class BusinessException(Exception):
    """业务异常，对应可预期的错误场景"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


# ---------- 常用错误码常量 ----------

class ErrCode:
    PARAM_ERROR = 40001
    UNAUTHORIZED = 40100
    TOKEN_EXPIRED = 40101
    TOKEN_REVOKED = 40102
    FORBIDDEN = 40300
    MERCHANT_NOT_APPROVED = 40301
    NOT_FOUND = 40400
    CONFLICT = 40900
    POINTS_INSUFFICIENT = 42200
    STOCK_INSUFFICIENT = 42201
    ACTIVITY_ENDED = 42202
    SERVER_ERROR = 50000


# ---------- 全局异常处理器 ----------

async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "message": exc.message, "data": None},
    )


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": ErrCode.SERVER_ERROR, "message": "服务器内部错误", "data": None},
    )
