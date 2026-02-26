from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
import jwt

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import BusinessException, ErrCode
from app.core.config import settings
from app.models.user import User
from app.models.merchant import Merchant
from app.models.points import PointsRecord, PointsRule


MOCK_SMS_CODE = "123456"


def svc_send_sms(phone: str) -> None:
    """Mock: 不实际发送，演示固定验证码 123456"""
    pass


def svc_register(db: Session, phone: str, password: str, sms_code: str) -> dict:
    if sms_code != MOCK_SMS_CODE:
        raise BusinessException(ErrCode.PARAM_ERROR, "短信验证码错误（演示固定：123456）")

    existing = db.query(User).filter(User.phone == phone, User.deleted_at.is_(None)).first()
    if existing:
        raise BusinessException(ErrCode.PARAM_ERROR, "该手机号已注册")

    user = User(
        phone=phone,
        password_hash=hash_password(password),
        nickname=f"用户{phone[-4:]}",
        role="user",
        points_balance=0,
    )
    db.add(user)
    db.flush()

    # 注册赠送积分
    rule = db.query(PointsRule).filter(
        PointsRule.rule_type == "register",
        PointsRule.is_active == 1,
        PointsRule.deleted_at.is_(None),
    ).first()
    gift_points = rule.points_amount if rule else 500

    record = PointsRecord(
        user_id=user.id,
        amount=gift_points,
        balance_after=gift_points,
        type="register",
        description="注册赠送积分",
    )
    user.points_balance = gift_points
    db.add(record)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"access_token": access_token, "refresh_token": refresh_token}


def svc_merchant_register(db: Session, phone: str, password: str, sms_code: str,
                           company_name: str, business_license: str) -> dict:
    if sms_code != MOCK_SMS_CODE:
        raise BusinessException(ErrCode.PARAM_ERROR, "短信验证码错误（演示固定：123456）")

    existing = db.query(User).filter(User.phone == phone, User.deleted_at.is_(None)).first()
    if existing:
        raise BusinessException(ErrCode.PARAM_ERROR, "该手机号已注册")

    user = User(
        phone=phone,
        password_hash=hash_password(password),
        nickname=company_name,
        role="merchant",
        points_balance=0,
    )
    db.add(user)
    db.flush()

    merchant = Merchant(
        user_id=user.id,
        merchant_name=company_name,
        contact_name=company_name,
        contact_phone=phone,
        business_license=business_license,
        status="pending",
    )
    db.add(merchant)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"access_token": access_token, "refresh_token": refresh_token}


def svc_login(db: Session, phone: str, password: str) -> dict:
    user = db.query(User).filter(User.phone == phone, User.deleted_at.is_(None)).first()
    if not user or not verify_password(password, user.password_hash):
        raise BusinessException(ErrCode.UNAUTHORIZED, "手机号或密码错误")
    if user.is_banned:
        raise BusinessException(ErrCode.FORBIDDEN, "账号已被封禁")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"access_token": access_token, "refresh_token": refresh_token}


def svc_refresh_token(db: Session, refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise BusinessException(ErrCode.UNAUTHORIZED, "无效的 refresh token")

    user = db.get(User, int(payload["sub"]))
    if not user or user.deleted_at:
        raise BusinessException(ErrCode.UNAUTHORIZED, "用户不存在")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token}


def svc_get_profile(db: Session, user_id: int) -> dict:
    user = db.get(User, user_id)
    if not user or user.deleted_at:
        raise BusinessException(ErrCode.NOT_FOUND, "用户不存在")

    merchant_id = None
    if user.role == "merchant":
        m = db.query(Merchant).filter(
            Merchant.user_id == user.id, Merchant.deleted_at.is_(None)
        ).first()
        merchant_id = m.id if m else None

    return {
        "id": user.id,
        "phone": user.phone,
        "nickname": user.nickname,
        "avatar": user.avatar_url,
        "role": user.role,
        "points_balance": user.points_balance,
        "merchant_id": merchant_id,
    }


def svc_update_profile(db: Session, user_id: int, nickname: Optional[str], avatar: Optional[str]) -> dict:
    user = db.get(User, user_id)
    if nickname:
        user.nickname = nickname
    if avatar:
        user.avatar_url = avatar
    db.commit()
    return svc_get_profile(db, user_id)


def svc_change_password(db: Session, user_id: int, old_password: str, new_password: str) -> None:
    user = db.get(User, user_id)
    if not verify_password(old_password, user.password_hash):
        raise BusinessException(ErrCode.PARAM_ERROR, "原密码错误")
    user.password_hash = hash_password(new_password)
    db.commit()
