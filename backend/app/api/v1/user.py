from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success, paginated
from app.schemas.misc import QuickRechargeRequest, AddressCreate
from app.services import user_service

router = APIRouter(tags=["points & user"])


# ---- Points ----
@router.get("/points/balance")
def points_balance(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    data = user_service.svc_points_balance(db, current_user.id)
    return success(data)


@router.get("/points/records")
def points_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = user_service.svc_points_records(db, current_user.id, page, page_size, type)
    return paginated(result["items"], result["total"], page, page_size)


@router.post("/points/quick-recharge")
def quick_recharge(body: QuickRechargeRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = user_service.svc_quick_recharge(db, current_user.id, body.phone, body.amount, body.type)
    return success(result)


@router.get("/points/recharge-history")
def recharge_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = user_service.svc_recharge_history(db, current_user.id, page, page_size)
    return paginated(result["items"], result["total"], page, page_size)


# ---- User Profile & Addresses ----
@router.get("/user/addresses")
def list_addresses(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    data = user_service.svc_list_addresses(db, current_user.id)
    return success(data)


@router.post("/user/addresses")
def add_address(body: AddressCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    data = user_service.svc_add_address(db, current_user.id, body.model_dump())
    return success(data)


@router.put("/user/addresses/{addr_id}")
def update_address(addr_id: int, body: AddressCreate,
                   current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    data = user_service.svc_update_address(db, current_user.id, addr_id, body.model_dump())
    return success(data)


@router.delete("/user/addresses/{addr_id}")
def delete_address(addr_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user_service.svc_delete_address(db, current_user.id, addr_id)
    return success({"message": "删除成功"})
