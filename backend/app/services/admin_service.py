from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.exceptions import BusinessException, ErrCode
from app.models.merchant import Merchant
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.activity import Activity, ActivityProduct, ActivityParticipant
from app.models.announcement import Announcement
from app.models.points import PointsRule


# -------- Merchant Dashboard --------
def svc_merchant_dashboard(db: Session, merchant_id: int) -> dict:
    total_products = db.query(Product).filter(
        Product.merchant_id == merchant_id, Product.deleted_at.is_(None)
    ).count()
    total_orders = db.query(Order).filter(
        Order.merchant_id == merchant_id, Order.deleted_at.is_(None)
    ).count()
    pending_orders = db.query(Order).filter(
        Order.merchant_id == merchant_id, Order.status == "paid", Order.deleted_at.is_(None)
    ).count()
    total_revenue = db.query(Order).filter(
        Order.merchant_id == merchant_id,
        Order.status.in_(["shipped", "completed"]),
        Order.deleted_at.is_(None),
    ).with_entities(Order.total_points).all()
    total_points = sum(r[0] for r in total_revenue)

    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_points_revenue": total_points,
    }


def svc_merchant_orders(db: Session, merchant_id: int, page: int = 1, page_size: int = 20,
                         status=None) -> dict:
    from app.services.order_service import STATUS_INT_TO_STR
    q = db.query(Order).filter(Order.merchant_id == merchant_id, Order.deleted_at.is_(None))
    if status is not None:
        s = STATUS_INT_TO_STR.get(status, str(status)) if isinstance(status, int) else status
        q = q.filter(Order.status == s)
    total = q.count()
    orders = q.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    from app.services.order_service import _order_to_dict
    items = [_order_to_dict(db, o, with_items=True) for o in orders]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


# -------- Admin --------
def svc_admin_users(db: Session, page: int = 1, page_size: int = 20, keyword: Optional[str] = None) -> dict:
    q = db.query(User).filter(User.deleted_at.is_(None))
    if keyword:
        q = q.filter(User.phone.like(f"%{keyword}%") | User.nickname.like(f"%{keyword}%"))
    total = q.count()
    users = q.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = [
        {
            "id": u.id, "phone": u.phone, "nickname": u.nickname,
            "role": u.role, "points_balance": u.points_balance,
            "is_banned": u.is_banned,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def svc_admin_merchants(db: Session, page: int = 1, page_size: int = 20,
                         status: Optional[str] = None) -> dict:
    q = db.query(Merchant).filter(Merchant.deleted_at.is_(None))
    if status is not None:
        q = q.filter(Merchant.status == status)
    total = q.count()
    merchants = q.order_by(Merchant.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = [
        {
            "id": m.id, "merchant_name": m.merchant_name,
            "contact_name": m.contact_name, "contact_phone": m.contact_phone,
            "business_license": m.business_license,
            "status": m.status, "user_id": m.user_id,
            "reject_reason": m.reject_reason,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in merchants
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def svc_admin_approve_merchant(db: Session, merchant_id: int, status: int, reason: Optional[str]) -> None:
    m = db.query(Merchant).filter(Merchant.id == merchant_id, Merchant.deleted_at.is_(None)).first()
    if not m:
        raise BusinessException(ErrCode.NOT_FOUND, "商家不存在")
    m.status = {1: "approved", 2: "rejected"}.get(status, "pending")
    if reason:
        m.reject_reason = reason
    db.commit()


def svc_admin_points_rules(db: Session) -> list:
    rules = db.query(PointsRule).filter(PointsRule.deleted_at.is_(None)).all()
    return [
        {
            "id": r.id, "name": r.name, "rule_type": r.rule_type,
            "points_amount": r.points_amount, "is_active": r.is_active,
        }
        for r in rules
    ]


def svc_admin_save_rule(db: Session, data: dict) -> dict:
    rule_id = data.pop("id", None)
    if rule_id:
        r = db.get(PointsRule, rule_id)
        if not r:
            raise BusinessException(ErrCode.NOT_FOUND, "规则不存在")
        for k, v in data.items():
            setattr(r, k, v)
    else:
        r = PointsRule(**data)
        db.add(r)
    db.commit()
    db.refresh(r)
    return {"id": r.id, "name": r.name}


# -------- Activities --------
def svc_list_activities(db: Session, page: int = 1, page_size: int = 10) -> dict:
    q = db.query(Activity).filter(Activity.deleted_at.is_(None), Activity.status == "active")
    total = q.count()
    acts = q.order_by(Activity.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = [
        {
            "id": a.id, "title": a.title, "type": a.type,
            "start_at": a.start_at.isoformat() if a.start_at else None,
            "end_at": a.end_at.isoformat() if a.end_at else None,
            "banner_url": a.banner_url,
        }
        for a in acts
    ]
    return {"items": items, "total": total}


def svc_get_activity(db: Session, activity_id: int) -> dict:
    a = db.query(Activity).filter(Activity.id == activity_id, Activity.deleted_at.is_(None)).first()
    if not a:
        raise BusinessException(ErrCode.NOT_FOUND, "活动不存在")
    # 关联商品
    ap_list = db.query(ActivityProduct).filter(ActivityProduct.activity_id == activity_id).all()
    products = []
    for ap in ap_list:
        p = db.get(Product, ap.product_id)
        if p and not p.deleted_at:
            products.append({"id": p.id, "name": p.name, "cover_image": p.cover_image,
                              "apply_status": ap.apply_status})
    return {
        "id": a.id, "title": a.title, "type": a.type,
        "start_at": a.start_at.isoformat() if a.start_at else None,
        "end_at": a.end_at.isoformat() if a.end_at else None,
        "banner_url": a.banner_url, "description": a.description,
        "products": products,
    }


# -------- Announcements --------
def svc_list_announcements(db: Session, page: int = 1, page_size: int = 10) -> dict:
    q = db.query(Announcement).filter(Announcement.deleted_at.is_(None))
    total = q.count()
    anns = q.order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = [
        {
            "id": a.id, "title": a.title, "content": a.content,
            "is_pinned": a.is_pinned,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in anns
    ]
    return {"items": items, "total": total}


def svc_admin_create_announcement(db: Session, admin_id: int, title: str, content: str, is_pinned: int = 0) -> dict:
    ann = Announcement(title=title, content=content, is_pinned=is_pinned, created_by=admin_id)
    db.add(ann)
    db.commit()
    db.refresh(ann)
    return {"id": ann.id, "title": ann.title}


def svc_admin_delete_announcement(db: Session, ann_id: int) -> None:
    ann = db.query(Announcement).filter(Announcement.id == ann_id, Announcement.deleted_at.is_(None)).first()
    if not ann:
        raise BusinessException(ErrCode.NOT_FOUND, "公告不存在")
    ann.deleted_at = datetime.now(timezone.utc)
    db.commit()
