# 导入所有模型，确保 Alembic 迁移时能发现所有表
from app.models.base import Base
from app.models.user import User
from app.models.merchant import Merchant
from app.models.address import Address
from app.models.product import Category, Product, ProductSku, ProductImage
from app.models.inventory import Inventory
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.points import PointsRule, PointsRecord
from app.models.review import Review
from app.models.activity import Activity, ActivityProduct, ActivityParticipant
from app.models.announcement import Announcement
from app.models.quick_recharge import PhoneRechargeOrder

__all__ = [
    "Base",
    "User",
    "Merchant",
    "Address",
    "Category",
    "Product",
    "ProductSku",
    "ProductImage",
    "Inventory",
    "CartItem",
    "Order",
    "OrderItem",
    "PointsRule",
    "PointsRecord",
    "Review",
    "Activity",
    "ActivityProduct",
    "ActivityParticipant",
    "Announcement",
    "PhoneRechargeOrder",
]
