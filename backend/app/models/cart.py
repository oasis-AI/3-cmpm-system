from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from app.models.base import Base, TimestampMixin


class CartItem(Base, TimestampMixin):
    __tablename__ = "cart_items"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(BIGINT(unsigned=True), nullable=False)
    product_id = Column(BIGINT(unsigned=True), nullable=False)
    sku_id = Column(BIGINT(unsigned=True), nullable=False)
    quantity = Column(INTEGER(unsigned=True), nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint("user_id", "sku_id", name="uk_user_sku"),
    )
