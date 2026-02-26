from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from app.models.base import Base, TimestampMixin


class Inventory(Base, TimestampMixin):
    __tablename__ = "inventory"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    sku_id = Column(BIGINT(unsigned=True), nullable=False, unique=True, comment="1:1 与 product_skus")
    product_id = Column(BIGINT(unsigned=True), nullable=False, comment="冗余，便于查询")
    quantity = Column(INTEGER(unsigned=True), nullable=False, default=0, comment="实际库存")
    locked_quantity = Column(
        INTEGER(unsigned=True), nullable=False, default=0, comment="已预占未发货"
    )
    low_stock_alert = Column(
        INTEGER(unsigned=True), nullable=False, default=10, comment="低库存预警阈值"
    )
