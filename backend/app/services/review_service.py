from typing import Optional
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ErrCode
from app.models.review import Review
from app.models.order import Order, OrderItem
from app.models.user import User


def svc_get_product_reviews(db: Session, product_id: int, page: int = 1, page_size: int = 10) -> dict:
    q = db.query(Review).filter(
        Review.product_id == product_id,
        Review.deleted_at.is_(None),
    )
    total = q.count()
    reviews = q.order_by(Review.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for r in reviews:
        user = db.get(User, r.user_id) if not r.is_anonymous else None
        items.append({
            "id": r.id,
            "rating": r.rating,
            "content": r.content,
            "is_anonymous": r.is_anonymous,
            "nickname": "匿名用户" if r.is_anonymous else (user.nickname if user else "已注销"),
            "avatar": None if r.is_anonymous else (user.avatar_url if user else None),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    # 统计
    avg_rating = None
    if total > 0:
        total_score = db.query(Review).filter(
            Review.product_id == product_id,
            Review.deleted_at.is_(None),
        ).with_entities(Review.rating).all()
        avg_rating = round(sum(r[0] for r in total_score) / total, 1)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "avg_rating": avg_rating,
    }


def svc_create_review(
    db: Session,
    user_id: int,
    order_id: int,
    order_item_id: int,
    rating: int,
    content: Optional[str],
    is_anonymous: bool = False,
) -> dict:
    # 校验订单归属 + 已完成
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id,
        Order.deleted_at.is_(None),
    ).first()
    if not order:
        raise BusinessException(ErrCode.NOT_FOUND, "订单不存在")
    if order.status != "completed":
        raise BusinessException(ErrCode.PARAM_ERROR, "订单未完成，暂不能评价")

    item = db.query(OrderItem).filter(
        OrderItem.id == order_item_id,
        OrderItem.order_id == order_id,
    ).first()
    if not item:
        raise BusinessException(ErrCode.NOT_FOUND, "订单商品不存在")

    # 防止重复评价
    existing = db.query(Review).filter(
        Review.order_item_id == order_item_id,
        Review.user_id == user_id,
        Review.deleted_at.is_(None),
    ).first()
    if existing:
        raise BusinessException(ErrCode.PARAM_ERROR, "该商品已评价")

    if not (1 <= rating <= 5):
        raise BusinessException(ErrCode.PARAM_ERROR, "评分需在 1-5 之间")

    review = Review(
        order_id=order_id,
        order_item_id=order_item_id,
        user_id=user_id,
        product_id=item.product_id,
        sku_id=item.sku_id,
        rating=rating,
        content=content,
        is_anonymous=1 if is_anonymous else 0,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"id": review.id, "message": "评价成功"}
