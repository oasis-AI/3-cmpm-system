from pydantic import BaseModel
from typing import Optional


class PointsRecordOut(BaseModel):
    id: int
    change_amount: int
    balance_after: int
    type: int
    description: Optional[str] = None
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


class QuickRechargeRequest(BaseModel):
    phone: str
    amount: int
    type: str = "phone"  # phone | data


class AddressOut(BaseModel):
    id: int
    receiver_name: str
    receiver_phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: int = 0

    model_config = {"from_attributes": True}


class AddressCreate(BaseModel):
    receiver_name: str
    receiver_phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: int = 0


class MerchantApproveRequest(BaseModel):
    status: int  # 1=approved, 2=rejected
    reason: Optional[str] = None
