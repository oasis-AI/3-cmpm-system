from sqlalchemy import Column, String, DECIMAL, DateTime, Text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from app.models.base import Base, TimestampMixin


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False, comment="订单号")
    user_id = Column(BIGINT(unsigned=True), nullable=False)
    merchant_id = Column(BIGINT(unsigned=True), nullable=False)
    total_points = Column(INTEGER(unsigned=True), nullable=False)
    total_cash = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="pending/paid/shipped/delivered/completed/cancelled/refunding/refunded",
    )
    receiver_name = Column(String(50), nullable=False, comment="快照：收件人")
    receiver_phone = Column(String(11), nullable=False)
    receiver_address = Column(String(300), nullable=False, comment="快照：完整地址")
    express_company = Column(String(50), nullable=True)
    express_no = Column(String(50), nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    remark = Column(String(500), nullable=True)


class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    order_id = Column(BIGINT(unsigned=True), nullable=False)
    product_id = Column(BIGINT(unsigned=True), nullable=False)
    sku_id = Column(BIGINT(unsigned=True), nullable=False)
    product_name = Column(String(200), nullable=False, comment="快照：商品名")
    sku_name = Column(String(200), nullable=False, comment="快照：规格名")
    cover_image = Column(String(500), nullable=False, comment="快照：主图")
    points_price = Column(INTEGER(unsigned=True), nullable=False, comment="快照：积分单价")
    cash_supplement = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    quantity = Column(INTEGER(unsigned=True), nullable=False, default=1)
