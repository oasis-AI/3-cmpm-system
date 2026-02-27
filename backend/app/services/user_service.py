import uuid
from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ErrCode
from app.models.user import User
from app.models.address import Address
from app.models.points import PointsRecord, PointsRule
from app.models.quick_recharge import PhoneRechargeOrder
from app.models.checkin import CheckIn


def svc_points_balance(db: Session, user_id: int) -> dict:
    user = db.get(User, user_id)
    return {"balance": user.points_balance if user else 0}


def svc_points_records(db: Session, user_id: int, page: int = 1, page_size: int = 20,
                       type: Optional[str] = None) -> dict:
    q = db.query(PointsRecord).filter(PointsRecord.user_id == user_id)
    if type is not None:
        q = q.filter(PointsRecord.type == type)
    total = q.count()
    records = q.order_by(PointsRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = [
        {
            "id": r.id,
            "amount": r.amount,
            "balance_after": r.balance_after,
            "type": r.type,
            "description": r.description,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def svc_quick_recharge(db: Session, user_id: int, phone: str, amount: int, recharge_type: str) -> dict:
    """话费/流量Mock充值：消耗对应积分，生成充值记录"""
    # 1元 = 100积分
    points_needed = amount * 100
    user = db.get(User, user_id)
    if not user or user.points_balance < points_needed:
        raise BusinessException(ErrCode.POINTS_INSUFFICIENT, f"积分不足，需要 {points_needed} 积分")

    user.points_balance -= points_needed
    rtype = "phone_recharge" if recharge_type == "phone" else "flow_recharge"
    db.add(PointsRecord(
        user_id=user_id,
        amount=-points_needed,
        balance_after=user.points_balance,
        type=rtype,
        description=f"{'话费' if recharge_type == 'phone' else '流量'}充值 {amount}元 → {phone}",
    ))

    order = PhoneRechargeOrder(
        user_id=user_id,
        phone_number=phone,
        package_name=f"{amount}元",
        recharge_type=recharge_type,
        points_cost=points_needed,
        status="success",
    )
    db.add(order)
    db.commit()
    return {
        "order_id": order.id,
        "phone": phone,
        "amount": amount,
        "points_cost": points_needed,
        "balance_after": user.points_balance,
    }


def svc_recharge_history(db: Session, user_id: int, page: int = 1, page_size: int = 20) -> dict:
    q = db.query(PhoneRechargeOrder).filter(PhoneRechargeOrder.user_id == user_id)
    total = q.count()
    records = q.order_by(PhoneRechargeOrder.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = [
        {
            "id": r.id,
            "order_no": r.order_no,
            "phone": r.phone,
            "amount": r.amount,
            "recharge_type": r.recharge_type,
            "points_cost": r.points_cost,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


# -------- Addresses --------
def svc_list_addresses(db: Session, user_id: int) -> list:
    addrs = db.query(Address).filter(
        Address.user_id == user_id,
        Address.deleted_at.is_(None),
    ).order_by(Address.is_default.desc(), Address.created_at.desc()).all()
    return [_addr_dict(a) for a in addrs]


def svc_add_address(db: Session, user_id: int, data: dict) -> dict:
    if data.get("is_default"):
        db.query(Address).filter(
            Address.user_id == user_id, Address.deleted_at.is_(None)
        ).update({"is_default": 0})
    addr = Address(user_id=user_id, **data)
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return _addr_dict(addr)


def svc_update_address(db: Session, user_id: int, addr_id: int, data: dict) -> dict:
    addr = db.query(Address).filter(
        Address.id == addr_id, Address.user_id == user_id, Address.deleted_at.is_(None)
    ).first()
    if not addr:
        raise BusinessException(ErrCode.NOT_FOUND, "地址不存在")
    if data.get("is_default"):
        db.query(Address).filter(
            Address.user_id == user_id, Address.deleted_at.is_(None)
        ).update({"is_default": 0})
    for k, v in data.items():
        setattr(addr, k, v)
    db.commit()
    return _addr_dict(addr)


def svc_delete_address(db: Session, user_id: int, addr_id: int) -> None:
    from datetime import datetime, timezone
    addr = db.query(Address).filter(
        Address.id == addr_id, Address.user_id == user_id, Address.deleted_at.is_(None)
    ).first()
    if not addr:
        raise BusinessException(ErrCode.NOT_FOUND, "地址不存在")
    addr.deleted_at = datetime.now(timezone.utc)
    db.commit()


def _addr_dict(a: Address) -> dict:
    return {
        "id": a.id,
        "receiver_name": a.receiver_name,
        "receiver_phone": a.receiver_phone,
        "province": a.province,
        "city": a.city,
        "district": a.district,
        "detail": a.detail,
        "is_default": a.is_default,
    }


# ---- 签到 ----

def _checkin_points(streak: int) -> int:
    """连签奖励：1-6天10分，7天翻倍20分，以7天为周期"""
    return 20 if streak % 7 == 0 else 10


def svc_checkin_status(db: Session, user_id: int) -> dict:
    today = date.today()
    today_record = db.query(CheckIn).filter(
        CheckIn.user_id == user_id,
        CheckIn.check_date == today,
        CheckIn.deleted_at.is_(None),
    ).first()

    # 计算当前连签天数
    streak = 0
    if today_record:
        streak = today_record.streak_days
    else:
        yesterday = db.query(CheckIn).filter(
            CheckIn.user_id == user_id,
            CheckIn.check_date == today - timedelta(days=1),
            CheckIn.deleted_at.is_(None),
        ).first()
        streak = (yesterday.streak_days if yesterday else 0)

    user = db.get(User, user_id)
    return {
        "checked_in_today": today_record is not None,
        "streak_days": streak if not today_record else today_record.streak_days,
        "next_points": _checkin_points((streak + 1) if not today_record else streak + 1),
        "points_balance": user.points_balance if user else 0,
    }


def svc_do_checkin(db: Session, user_id: int) -> dict:
    today = date.today()
    existing = db.query(CheckIn).filter(
        CheckIn.user_id == user_id,
        CheckIn.check_date == today,
        CheckIn.deleted_at.is_(None),
    ).first()
    if existing:
        raise BusinessException(ErrCode.PARAM_ERROR, "今日已签到")

    # 计算连签天数
    yesterday_rec = db.query(CheckIn).filter(
        CheckIn.user_id == user_id,
        CheckIn.check_date == today - timedelta(days=1),
        CheckIn.deleted_at.is_(None),
    ).first()
    streak = (yesterday_rec.streak_days + 1) if yesterday_rec else 1
    points = _checkin_points(streak)

    user = db.get(User, user_id)
    if not user:
        raise BusinessException(ErrCode.NOT_FOUND, "用户不存在")

    user.points_balance += points
    db.add(CheckIn(
        user_id=user_id,
        check_date=today,
        points_earned=points,
        streak_days=streak,
    ))
    db.add(PointsRecord(
        user_id=user_id,
        type="checkin",
        amount=points,
        balance_after=user.points_balance,
        description=f"每日签到（连签第{streak}天）",
    ))
    db.commit()

    return {
        "points_earned": points,
        "streak_days": streak,
        "balance_after": user.points_balance,
        "message": f"签到成功！获得 {points} 积分，连签第 {streak} 天",
    }
