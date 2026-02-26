from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal


class CartItemOut(BaseModel):
    id: int
    sku_id: int
    product_id: int
    product_name: str
    sku_name: str
    points_price: int
    quantity: int
    main_image: Optional[str] = None
    subtotal_points: int = 0

    model_config = {"from_attributes": True}


class AddCartRequest(BaseModel):
    sku_id: int
    quantity: int = 1


class UpdateCartRequest(BaseModel):
    quantity: int


class OrderItemOut(BaseModel):
    id: int
    product_name: str
    sku_name: str
    points_price: int
    quantity: int
    subtotal_points: int
    main_image: Optional[str] = None

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    order_no: str
    total_points: int
    status: int
    status_label: str = ""
    address_snapshot: Optional[dict] = None
    items: List[OrderItemOut] = []
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}


class CreateOrderRequest(BaseModel):
    sku_id: int
    quantity: int = 1
    address_id: int


class ShipRequest(BaseModel):
    express_company: str
    express_no: str
