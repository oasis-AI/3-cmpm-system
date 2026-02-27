from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_merchant, require_admin
from app.core.response import success, paginated
from app.schemas.misc import MerchantApproveRequest
from app.services import admin_service

router = APIRouter(tags=["merchant & admin"])


# ---- Merchant Dashboard ----
@router.get("/merchant/dashboard")
def merchant_dashboard(current_user=Depends(require_merchant), db: Session = Depends(get_db)):
    from app.models.merchant import Merchant
    m = db.query(Merchant).filter(Merchant.user_id == current_user.id, Merchant.deleted_at.is_(None)).first()
    data = admin_service.svc_merchant_dashboard(db, m.id if m else -1)
    return success(data)


@router.put("/merchant/info")
def update_merchant_info(body: dict, current_user=Depends(require_merchant), db: Session = Depends(get_db)):
    from app.models.merchant import Merchant
    m = db.query(Merchant).filter(Merchant.user_id == current_user.id, Merchant.deleted_at.is_(None)).first()
    if m:
        for k, v in body.items():
            if hasattr(m, k):
                setattr(m, k, v)
        db.commit()
    return success({"message": "更新成功"})


# ---- Admin ----
@router.get("/admin/users")
def admin_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    result = admin_service.svc_admin_users(db, page, page_size, keyword)
    return paginated(result["items"], result["total"], page, page_size)


@router.get("/admin/merchants")
def admin_merchants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    result = admin_service.svc_admin_merchants(db, page, page_size, status)
    return paginated(result["items"], result["total"], page, page_size)


@router.post("/admin/merchants/{merchant_id}/approve")
def admin_approve_merchant(
    merchant_id: int,
    body: MerchantApproveRequest,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    admin_service.svc_admin_approve_merchant(db, merchant_id, body.status, body.reason)
    return success({"message": "审批成功"})


@router.get("/admin/points-rules")
def admin_points_rules(current_user=Depends(require_admin), db: Session = Depends(get_db)):
    data = admin_service.svc_admin_points_rules(db)
    return success(data)


@router.post("/admin/points-rules")
def admin_create_rule(body: dict, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    data = admin_service.svc_admin_save_rule(db, body)
    return success(data)


@router.put("/admin/points-rules/{rule_id}")
def admin_update_rule(rule_id: int, body: dict, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    body["id"] = rule_id
    data = admin_service.svc_admin_save_rule(db, body)
    return success(data)


@router.get("/admin/orders")
def admin_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = None,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    from app.models.order import Order
    q = db.query(Order).filter(Order.deleted_at.is_(None))
    if status is not None:
        q = q.filter(Order.status == status)
    total = q.count()
    orders = q.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    from app.services.order_service import _order_to_dict
    items = [_order_to_dict(db, o) for o in orders]
    return paginated(items, total, page, page_size)


@router.get("/admin/announcements")
def admin_list_announcements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    result = admin_service.svc_list_announcements(db, page, page_size)
    return paginated(result["items"], result["total"], page, page_size)


@router.post("/admin/announcements")
def admin_create_announcement(body: dict, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    data = admin_service.svc_admin_create_announcement(
        db, current_user.id,
        body.get("title", ""), body.get("content", ""), body.get("is_pinned", 0)
    )
    return success(data)


@router.put("/admin/announcements/{ann_id}")
def admin_update_announcement(ann_id: int, body: dict, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    from app.models.announcement import Announcement
    ann = db.query(Announcement).filter(Announcement.id == ann_id, Announcement.deleted_at.is_(None)).first()
    if ann:
        for k in ("title", "content", "is_pinned"):
            if k in body:
                setattr(ann, k, body[k])
        db.commit()
    return success({"message": "更新成功"})


@router.delete("/admin/announcements/{ann_id}")
def admin_delete_announcement(ann_id: int, current_user=Depends(require_admin), db: Session = Depends(get_db)):
    admin_service.svc_admin_delete_announcement(db, ann_id)
    return success({"message": "删除成功"})


# ---- Activities (public read, admin write) ----
@router.get("/activities")
def list_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    result = admin_service.svc_list_activities(db, page, page_size)
    return paginated(result["items"], result["total"], page, page_size)


@router.get("/activities/{activity_id}")
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    data = admin_service.svc_get_activity(db, activity_id)
    return success(data)


@router.get("/announcements")
def list_announcements(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    result = admin_service.svc_list_announcements(db, page, page_size)
    return paginated(result["items"], result["total"], page, page_size)
