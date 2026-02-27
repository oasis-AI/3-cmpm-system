import uuid
from typing import Optional
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ErrCode
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.product import Product, ProductSku
from app.models.user import User
from app.models.points import PointsRecord
from app.models.address import Address
from app.models.inventory import Inventory


ORDER_STATUS = {
    "pending": "待支付",
    "paid": "已支付",
    "shipped": "已发货",
    "completed": "已完成",
    "cancelled": "已取消",
}

# compat: int → string (for API query params)
STATUS_INT_TO_STR = {0: "pending", 1: "paid", 2: "shipped", 3: "completed", 4: "cancelled"}


# -------- Cart --------
def svc_list_cart(db: Session, user_id: int) -> list:
    items = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.deleted_at.is_(None),
    ).all()

    result = []
    for item in items:
        sku = db.get(ProductSku, item.sku_id)
        p = db.get(Product, item.product_id) if sku else None
        if not sku or not p or p.deleted_at:
            continue
        result.append({
            "id": item.id,
            "sku_id": item.sku_id,
            "product_id": item.product_id,
            "product_name": p.name,
            "sku_name": sku.sku_name,
            "points_price": sku.points_price,
            "quantity": item.quantity,
            "cover_image": p.cover_image,
            "subtotal_points": sku.points_price * item.quantity,
        })
    return result


def svc_add_cart(db: Session, user_id: int, sku_id: int, quantity: int) -> dict:
    sku = db.get(ProductSku, sku_id)
    if not sku or sku.deleted_at:
        raise BusinessException(ErrCode.NOT_FOUND, "商品规格不存在")
    p = db.get(Product, sku.product_id)
    if not p or p.deleted_at or p.status != "on_sale":
        raise BusinessException(ErrCode.PARAM_ERROR, "商品已下架")

    existing = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.sku_id == sku_id,
        CartItem.deleted_at.is_(None),
    ).first()
    if existing:
        existing.quantity += quantity
    else:
        db.add(CartItem(
            user_id=user_id,
            sku_id=sku_id,
            product_id=sku.product_id,
            quantity=quantity,
        ))
    db.commit()
    return {"total": _cart_count(db, user_id)}


def svc_update_cart(db: Session, user_id: int, item_id: int, quantity: int) -> None:
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == user_id,
        CartItem.deleted_at.is_(None),
    ).first()
    if not item:
        raise BusinessException(ErrCode.NOT_FOUND, "购物车项不存在")
    item.quantity = quantity
    db.commit()


def svc_remove_cart(db: Session, user_id: int, item_id: int) -> None:
    from datetime import datetime, timezone
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == user_id,
        CartItem.deleted_at.is_(None),
    ).first()
    if not item:
        raise BusinessException(ErrCode.NOT_FOUND, "购物车项不存在")
    item.deleted_at = datetime.now(timezone.utc)
    db.commit()


def svc_clear_cart(db: Session, user_id: int) -> None:
    from datetime import datetime, timezone
    db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.deleted_at.is_(None),
    ).update({"deleted_at": datetime.now(timezone.utc)})
    db.commit()


def _cart_count(db: Session, user_id: int) -> int:
    return db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.deleted_at.is_(None),
    ).count()


# -------- Orders --------
def svc_create_order(db: Session, user_id: int, sku_id: int, quantity: int, address_id: int) -> dict:
    sku = db.get(ProductSku, sku_id)
    if not sku or sku.deleted_at:
        raise BusinessException(ErrCode.NOT_FOUND, "商品规格不存在")

    p = db.get(Product, sku.product_id)
    if not p or p.deleted_at or p.status != "on_sale":
        raise BusinessException(ErrCode.PARAM_ERROR, "商品已下架")

    # 检查库存
    inv = db.query(Inventory).filter(Inventory.sku_id == sku_id).first()
    if not inv or (inv.quantity - inv.locked_quantity) < quantity:
        raise BusinessException(ErrCode.STOCK_INSUFFICIENT, "库存不足")

    # 检查积分
    user = db.get(User, user_id)
    total_points = sku.points_price * quantity
    if user.points_balance < total_points:
        raise BusinessException(ErrCode.POINTS_INSUFFICIENT, "积分余额不足")

    # 地址快照
    addr = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id,
        Address.deleted_at.is_(None),
    ).first()
    if not addr:
        raise BusinessException(ErrCode.NOT_FOUND, "收货地址不存在")

    addr_snapshot = {
        "receiver_name": addr.receiver_name,
        "receiver_phone": addr.receiver_phone,
        "address": f"{addr.province}{addr.city}{addr.district}{addr.detail}",
    }

    # 创建订单
    order_no = f"ORD{uuid.uuid4().hex[:16].upper()}"
    order = Order(
        order_no=order_no,
        user_id=user_id,
        merchant_id=p.merchant_id,
        total_points=total_points,
        total_cash=0.00,
        status="paid",  # 积分即时扣除，直接付款
        receiver_name=addr.receiver_name,
        receiver_phone=addr.receiver_phone,
        receiver_address=f"{addr.province}{addr.city}{addr.district}{addr.detail}",
    )
    db.add(order)
    db.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=p.id,
        sku_id=sku.id,
        product_name=p.name,
        sku_name=sku.sku_name,
        points_price=sku.points_price,
        quantity=quantity,
        cover_image=p.cover_image,
    )
    db.add(order_item)

    # 扣积分
    user.points_balance -= total_points
    db.add(PointsRecord(
        user_id=user_id,
        amount=-total_points,
        balance_after=user.points_balance,
        type="exchange",
        description=f"兑换商品：{p.name}",
        ref_id=order.id,
    ))

    # 扣库存（锁定）
    inv.locked_quantity += quantity

    # 商品销量
    p.total_sales = (p.total_sales or 0) + quantity

    db.commit()
    return svc_get_order(db, order.id, user_id)


def svc_list_orders(db: Session, user_id: int, page: int = 1, page_size: int = 10,
                    status=None) -> dict:
    q = db.query(Order).filter(Order.user_id == user_id, Order.deleted_at.is_(None))
    if status is not None:
        status_str = STATUS_INT_TO_STR.get(status, str(status)) if isinstance(status, int) else status
        q = q.filter(Order.status == status_str)
    total = q.count()
    orders = q.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = [_order_to_dict(db, o, with_items=True) for o in orders]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def svc_get_order(db: Session, order_id: int, user_id: Optional[int] = None) -> dict:
    q = db.query(Order).filter(Order.id == order_id, Order.deleted_at.is_(None))
    if user_id:
        q = q.filter(Order.user_id == user_id)
    o = q.first()
    if not o:
        raise BusinessException(ErrCode.NOT_FOUND, "订单不存在")
    return _order_to_dict(db, o, with_items=True)


def _order_to_dict(db: Session, o: Order, with_items: bool = False) -> dict:
    d = {
        "id": o.id,
        "order_no": o.order_no,
        "total_points": o.total_points,
        "status": o.status,
        "status_label": ORDER_STATUS.get(o.status, o.status),
        "receiver_name": o.receiver_name,
        "receiver_phone": o.receiver_phone,
        "receiver_address": o.receiver_address,
        "express_company": o.express_company,
        "express_no": o.express_no,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }
    if with_items:
        items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
        d["items"] = [
            {
                "id": it.id,
                "product_name": it.product_name,
                "sku_name": it.sku_name,
                "points_price": it.points_price,
                "quantity": it.quantity,
                "subtotal_points": it.points_price * it.quantity,
                "cover_image": it.cover_image,
            }
            for it in items
        ]
    return d


def svc_cancel_order(db: Session, order_id: int, user_id: int) -> None:
    o = db.query(Order).filter(
        Order.id == order_id, Order.user_id == user_id, Order.deleted_at.is_(None)
    ).first()
    if not o:
        raise BusinessException(ErrCode.NOT_FOUND, "订单不存在")
    if o.status not in ("pending", "paid"):
        raise BusinessException(ErrCode.PARAM_ERROR, "订单状态不允许取消")

    # 退积分
    user = db.get(User, user_id)
    user.points_balance += o.total_points
    db.add(PointsRecord(
        user_id=user_id,
        amount=o.total_points,
        balance_after=user.points_balance,
        type="refund",
        description=f"订单取消退款：{o.order_no}",
        ref_id=o.id,
    ))

    # 释放库存
    items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
    for it in items:
        inv = db.query(Inventory).filter(Inventory.sku_id == it.sku_id).first()
        if inv:
            inv.locked_quantity = max(0, inv.locked_quantity - it.quantity)

    o.status = "cancelled"
    db.commit()


def svc_confirm_order(db: Session, order_id: int, user_id: int) -> None:
    o = db.query(Order).filter(
        Order.id == order_id, Order.user_id == user_id, Order.deleted_at.is_(None)
    ).first()
    if not o:
        raise BusinessException(ErrCode.NOT_FOUND, "订单不存在")
    if o.status != "shipped":
        raise BusinessException(ErrCode.PARAM_ERROR, "订单未发货，无法确认收货")
    o.status = "completed"

    # 更新库存（锁定→出售）
    items = db.query(OrderItem).filter(OrderItem.order_id == o.id).all()
    for it in items:
        inv = db.query(Inventory).filter(Inventory.sku_id == it.sku_id).first()
        if inv:
            inv.locked_stock = max(0, inv.locked_stock - it.quantity)

    db.commit()


def svc_ship_order(db: Session, order_id: int, merchant_id: int,
                   express_company: str, express_no: str) -> None:
    o = db.query(Order).filter(
        Order.id == order_id,
        Order.merchant_id == merchant_id,
        Order.deleted_at.is_(None),
    ).first()
    if not o:
        raise BusinessException(ErrCode.NOT_FOUND, "订单不存在或无权限")
    if o.status != "paid":
        raise BusinessException(ErrCode.PARAM_ERROR, "订单状态不允许发货")
    o.status = "shipped"
    o.express_company = express_company
    o.express_no = express_no
    db.commit()
