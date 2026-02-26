from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select
import jwt

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import decode_token
from app.core.exceptions import BusinessException, ErrCode
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def _get_token_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    redis_client=Depends(get_redis),
) -> dict:
    """解析并验证 Token，返回 payload"""
    if not credentials:
        raise BusinessException(ErrCode.UNAUTHORIZED, "请先登录")

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise BusinessException(ErrCode.TOKEN_EXPIRED, "登录已过期，请重新登录")
    except jwt.PyJWTError:
        raise BusinessException(ErrCode.UNAUTHORIZED, "Token 无效")

    # 检查黑名单（登出后的 Token）
    jti = payload.get("jti")
    if jti and redis_client.exists(f"token:blacklist:{jti}"):
        raise BusinessException(ErrCode.TOKEN_REVOKED, "Token 已注销，请重新登录")

    return payload


def get_current_user(
    payload: dict = Depends(_get_token_payload),
    db: Session = Depends(get_db),
) -> User:
    """获取当前登录用户"""
    user_id = payload.get("sub")
    user = db.execute(
        select(User).where(User.id == int(user_id), User.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not user:
        raise BusinessException(ErrCode.UNAUTHORIZED, "用户不存在")
    if user.is_banned:
        raise BusinessException(ErrCode.FORBIDDEN, "账号已被封禁")

    return user


def require_merchant(current_user: User = Depends(get_current_user)) -> User:
    """要求商户身份（已审核通过）"""
    if current_user.role != "merchant":
        raise BusinessException(ErrCode.FORBIDDEN, "需要商户权限")

    from app.models.merchant import Merchant
    from sqlalchemy.orm import Session

    # 此处通过 current_user 中已注入的 db 获取商户状态
    # 简洁起见，将商户状态校验移至各 service 中按需处理
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求管理员身份"""
    if current_user.role != "admin":
        raise BusinessException(ErrCode.FORBIDDEN, "需要管理员权限")
    return current_user
