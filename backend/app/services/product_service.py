from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.exceptions import BusinessException, ErrCode
from app.models.product import Product, ProductSku, Category, ProductImage
from app.models.inventory import Inventory


def svc_list_categories(db: Session) -> List[dict]:
    cats = db.query(Category).filter(Category.deleted_at.is_(None)).order_by(Category.sort_order).all()
    return [{"id": c.id, "name": c.name, "icon": c.icon_url, "sort_order": c.sort_order} for c in cats]


def svc_list_products(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    sort: str = "default",
    min_points: Optional[int] = None,
    max_points: Optional[int] = None,
    merchant_id: Optional[int] = None,
    status: Optional[str] = None,
) -> dict:
    query = db.query(Product).filter(Product.deleted_at.is_(None))
    if status is not None:
        query = query.filter(Product.status == status)
    elif merchant_id is None:
        query = query.filter(Product.status == "on_sale")
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if keyword:
        query = query.filter(Product.name.like(f"%{keyword}%"))
    if min_points:
        query = query.filter(Product.min_points >= min_points)
    if max_points:
        query = query.filter(Product.min_points <= max_points)
    if merchant_id:
        query = query.filter(Product.merchant_id == merchant_id)
    if sort == "points_asc":
        query = query.order_by(Product.min_points.asc())
    elif sort == "points_desc":
        query = query.order_by(Product.min_points.desc())
    elif sort == "sales":
        query = query.order_by(Product.total_sales.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    total = query.count()
    products = query.offset((page - 1) * page_size).limit(page_size).all()

    # 批量获取分类名和商家名
    cat_ids = list({p.category_id for p in products})
    cat_map = {}
    if cat_ids:
        cats = db.query(Category).filter(Category.id.in_(cat_ids)).all()
        cat_map = {c.id: c.name for c in cats}

    items = []
    for p in products:
        # 取最低价 SKU
        min_sku = db.query(ProductSku).filter(
            ProductSku.product_id == p.id,
            ProductSku.deleted_at.is_(None),
        ).order_by(ProductSku.points_price.asc()).first()

        skus_data = []
        if merchant_id:
            all_skus = db.query(ProductSku).filter(
                ProductSku.product_id == p.id,
                ProductSku.deleted_at.is_(None),
            ).all()
            skus_data = [
                {
                    "id": s.id,
                    "sku_name": s.sku_name,
                    "points_price": s.points_price,
                    "stock": _sku_available_stock(db, s.id),
                }
                for s in all_skus
            ]

        items.append({
            "id": p.id,
            "name": p.name,
            "category_id": p.category_id,
            "category_name": cat_map.get(p.category_id),
            "merchant_id": p.merchant_id,
            "cover_image": p.cover_image,
            "points_price": min_sku.points_price if min_sku else p.min_points,
            "sales_count": p.total_sales,
            "status": p.status,
            "brand": p.brand,
            "tags": p.tags,
            "good_review_rate": float(p.good_review_rate),
            **({"skus": skus_data} if merchant_id else {}),
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


def svc_get_product(db: Session, product_id: int) -> dict:
    p = db.query(Product).filter(
        Product.id == product_id,
        Product.deleted_at.is_(None),
    ).first()
    if not p:
        raise BusinessException(ErrCode.NOT_FOUND, "商品不存在")

    skus = db.query(ProductSku).filter(
        ProductSku.product_id == p.id,
        ProductSku.deleted_at.is_(None),
    ).all()

    images = db.query(ProductImage).filter(
        ProductImage.product_id == p.id,
    ).order_by(ProductImage.sort_order).all()

    cat = db.get(Category, p.category_id)

    return {
        "id": p.id,
        "name": p.name,
        "category_id": p.category_id,
        "category_name": cat.name if cat else None,
        "merchant_id": p.merchant_id,
        "description": p.description,
        "cover_image": p.cover_image,
        "points_price": p.min_points,
        "sales_count": p.total_sales,
        "status": p.status,
        "images": [{"url": img.image_url, "sort": img.sort_order} for img in images],
        "skus": [
            {
                "id": s.id,
                "sku_name": s.sku_name,
                "points_price": s.points_price,
                "cash_supplement": float(s.cash_supplement),
                "stock": _sku_available_stock(db, s.id),
            }
            for s in skus
        ],
    }


def _sku_available_stock(db: Session, sku_id: int) -> int:
    inv = db.query(Inventory).filter(Inventory.sku_id == sku_id).first()
    if not inv:
        return 0
    return max(0, inv.quantity - inv.locked_quantity)


def svc_merchant_create_product(db: Session, merchant_id: int, data: dict) -> dict:
    skus_data = data.pop("skus", [])
    product = Product(
        merchant_id=merchant_id,
        name=data["name"],
        category_id=data.get("category_id") or 0,
        description=data.get("description"),
        cover_image=data.get("cover_image", ""),
        min_points=data.get("points_price", 0),
        brand=data.get("brand"),
        tags=data.get("tags"),
        status="pending",
    )
    db.add(product)
    db.flush()

    for s in skus_data:
        sku = ProductSku(
            product_id=product.id,
            sku_name=s.get("sku_name", "默认规格"),
            points_price=s.get("points_price", data.get("points_price", 0)),
        )
        db.add(sku)

    db.commit()
    return svc_get_product(db, product.id)


def svc_merchant_update_product(db: Session, product_id: int, merchant_id: int, data: dict) -> dict:
    p = db.query(Product).filter(
        Product.id == product_id,
        Product.merchant_id == merchant_id,
        Product.deleted_at.is_(None),
    ).first()
    if not p:
        raise BusinessException(ErrCode.NOT_FOUND, "商品不存在或无权限")

    field_map = {"points_price": "min_points", "main_image": "cover_image"}
    allowed = ("name", "category_id", "description", "cover_image", "min_points", "brand", "tags")
    for k, v in data.items():
        col = field_map.get(k, k)
        if col in allowed and v is not None:
            setattr(p, col, v)
    db.commit()
    return svc_get_product(db, product_id)


def svc_merchant_delete_product(db: Session, product_id: int, merchant_id: int) -> None:
    from datetime import datetime, timezone
    p = db.query(Product).filter(
        Product.id == product_id,
        Product.merchant_id == merchant_id,
        Product.deleted_at.is_(None),
    ).first()
    if not p:
        raise BusinessException(ErrCode.NOT_FOUND, "商品不存在或无权限")
    p.deleted_at = datetime.now(timezone.utc)
    db.commit()


def svc_merchant_toggle_status(db: Session, product_id: int, merchant_id: int, status: int) -> None:
    p = db.query(Product).filter(
        Product.id == product_id,
        Product.merchant_id == merchant_id,
        Product.deleted_at.is_(None),
    ).first()
    if not p:
        raise BusinessException(ErrCode.NOT_FOUND, "商品不存在或无权限")
    status_str = {1: "on_sale", 0: "off_shelf"}.get(status, str(status))
    p.status = status_str
    db.commit()
