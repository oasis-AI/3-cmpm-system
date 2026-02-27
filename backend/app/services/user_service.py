import uuid
from typing import Optional
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ErrCode
from app.models.user import User
from app.models.address import Address
from app.models.points import PointsRecord, PointsRule
from app.models.quick_recharge import PhoneRechargeOrder


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
