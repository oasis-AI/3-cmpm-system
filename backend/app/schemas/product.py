from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal


class SkuOut(BaseModel):
    id: int
    sku_name: str
    sku_code: str
    points_price: int
    original_price: Optional[Decimal] = None
    stock: int = 0

    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: int
    name: str
    category_id: int
    category_name: Optional[str] = None
    merchant_id: int
    merchant_name: Optional[str] = None
    description: Optional[str] = None
    main_image: Optional[str] = None
    points_price: int
    original_price: Optional[Decimal] = None
    sales_count: int = 0
    status: int = 1
    skus: List[SkuOut] = []

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    name: str = Field(..., max_length=200)
    category_id: int
    description: Optional[str] = None
    main_image: Optional[str] = None
    points_price: int = Field(..., ge=1)
    original_price: Optional[Decimal] = None
    skus: List[dict] = []


class ProductUpdate(ProductCreate):
    pass


class CategoryOut(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None
    sort_order: int = 0

    model_config = {"from_attributes": True}
