from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success, paginated
from app.schemas.order import AddCartRequest, UpdateCartRequest, CreateOrderRequest, ShipRequest
from app.services import order_service, review_service

router = APIRouter(tags=["cart & orders"])


# ---- Cart ----
@router.get("/cart")
def list_cart(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    items = order_service.svc_list_cart(db, current_user.id)
    return success(items)


@router.post("/cart")
def add_cart(body: AddCartRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = order_service.svc_add_cart(db, current_user.id, body.sku_id, body.quantity)
    return success(result)


@router.put("/cart/{item_id}")
def update_cart(item_id: int, body: UpdateCartRequest,
                current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    order_service.svc_update_cart(db, current_user.id, item_id, body.quantity)
    return success({"message": "更新成功"})


@router.delete("/cart/{item_id}")
def remove_cart(item_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    order_service.svc_remove_cart(db, current_user.id, item_id)
    return success({"message": "删除成功"})


@router.delete("/cart")
def clear_cart(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    order_service.svc_clear_cart(db, current_user.id)
    return success({"message": "清空成功"})


# ---- Orders ----
@router.post("/orders")
def create_order(body: CreateOrderRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    order = order_service.svc_create_order(db, current_user.id, body.sku_id, body.quantity, body.address_id)
    return success(order)


@router.get("/orders")
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = order_service.svc_list_orders(db, current_user.id, page, page_size, status)
    return paginated(result["items"], result["total"], page, page_size)


@router.get("/orders/{order_id}")
def get_order(order_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    order = order_service.svc_get_order(db, order_id, current_user.id)
    return success(order)


@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    order_service.svc_cancel_order(db, order_id, current_user.id)
    return success({"message": "订单已取消"})


@router.post("/orders/{order_id}/confirm")
def confirm_order(order_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    order_service.svc_confirm_order(db, order_id, current_user.id)
    return success({"message": "确认收货成功"})


# ---- Merchant Orders ----
@router.get("/merchant/orders")
def merchant_list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    status: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.merchant import Merchant
    from app.services import admin_service
    m = db.query(Merchant).filter(Merchant.user_id == current_user.id, Merchant.deleted_at.is_(None)).first()
    result = admin_service.svc_merchant_orders(db, m.id if m else -1, page, page_size, status)
    return paginated(result["items"], result["total"], page, page_size)


@router.post("/merchant/orders/{order_id}/ship")
def ship_order(order_id: int, body: ShipRequest,
               current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.merchant import Merchant
    m = db.query(Merchant).filter(Merchant.user_id == current_user.id, Merchant.deleted_at.is_(None)).first()
    order_service.svc_ship_order(db, order_id, m.id if m else -1, body.express_company, body.express_no)
    return success({"message": "发货成功"})


# ---- Reviews ----
@router.post("/orders/{order_id}/items/{item_id}/review")
def create_review(
    order_id: int,
    item_id: int,
    body: dict,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = review_service.svc_create_review(
        db,
        user_id=current_user.id,
        order_id=order_id,
        order_item_id=item_id,
        rating=body.get("rating", 5),
        content=body.get("content"),
        is_anonymous=body.get("is_anonymous", False),
    )
    return success(result)
