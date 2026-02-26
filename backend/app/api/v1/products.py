from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_merchant
from app.core.response import success, paginated
from app.services import product_service

router = APIRouter(tags=["products"])


@router.get("/products/categories")
def list_categories(db: Session = Depends(get_db)):
    data = product_service.svc_list_categories(db)
    return success(data)


@router.get("/products")
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    sort: str = "default",
    min_points: Optional[int] = None,
    max_points: Optional[int] = None,
    db: Session = Depends(get_db),
):
    result = product_service.svc_list_products(
        db, page=page, page_size=page_size,
        category_id=category_id, keyword=keyword,
        sort=sort, min_points=min_points, max_points=max_points,
    )
    return paginated(result["items"], result["total"], page, page_size)


@router.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    data = product_service.svc_get_product(db, product_id)
    return success(data)


# ---- Merchant B端 ----
@router.get("/merchant/products")
def merchant_list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = None,
    current_user=Depends(require_merchant),
    db: Session = Depends(get_db),
):
    from app.models.merchant import Merchant
    m = db.query(Merchant).filter(
        Merchant.user_id == current_user.id, Merchant.deleted_at.is_(None)
    ).first()
    result = product_service.svc_list_products(
        db, page=page, page_size=page_size,
        merchant_id=m.id if m else -1, status=status,
    )
    return paginated(result["items"], result["total"], page, page_size)


@router.post("/merchant/products")
def merchant_create_product(
    body: dict,
    current_user=Depends(require_merchant),
    db: Session = Depends(get_db),
):
    from app.models.merchant import Merchant
    m = db.query(Merchant).filter(
        Merchant.user_id == current_user.id, Merchant.deleted_at.is_(None)
    ).first()
    data = product_service.svc_merchant_create_product(db, m.id if m else 0, body)
    return success(data)


@router.put("/merchant/products/{product_id}")
def merchant_update_product(
    product_id: int,
    body: dict,
    current_user=Depends(require_merchant),
    db: Session = Depends(get_db),
):
    from app.models.merchant import Merchant
    m = db.query(Merchant).filter(
        Merchant.user_id == current_user.id, Merchant.deleted_at.is_(None)
    ).first()
    data = product_service.svc_merchant_update_product(db, product_id, m.id if m else 0, body)
    return success(data)


@router.delete("/merchant/products/{product_id}")
def merchant_delete_product(
    product_id: int,
    current_user=Depends(require_merchant),
    db: Session = Depends(get_db),
):
    from app.models.merchant import Merchant
    m = db.query(Merchant).filter(
        Merchant.user_id == current_user.id, Merchant.deleted_at.is_(None)
    ).first()
    product_service.svc_merchant_delete_product(db, product_id, m.id if m else 0)
    return success({"message": "删除成功"})


@router.patch("/merchant/products/{product_id}/status")
def merchant_toggle_status(
    product_id: int,
    body: dict,
    current_user=Depends(require_merchant),
    db: Session = Depends(get_db),
):
    from app.models.merchant import Merchant
    m = db.query(Merchant).filter(
        Merchant.user_id == current_user.id, Merchant.deleted_at.is_(None)
    ).first()
    product_service.svc_merchant_toggle_status(db, product_id, m.id if m else 0, body.get("status", 0))
    return success({"message": "状态更新成功"})
