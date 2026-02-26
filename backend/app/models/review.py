from sqlalchemy import Column, String, DECIMAL, Text, DateTime, Integer
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from app.models.base import Base, TimestampMixin


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    order_id = Column(BIGINT(unsigned=True), nullable=False)
    order_item_id = Column(BIGINT(unsigned=True), nullable=False)
    user_id = Column(BIGINT(unsigned=True), nullable=False)
    product_id = Column(BIGINT(unsigned=True), nullable=False)
    sku_id = Column(BIGINT(unsigned=True), nullable=False)
    rating = Column(TINYINT(unsigned=True), nullable=False, comment="评分 1-5")
    content = Column(String(1000), nullable=True)
    is_anonymous = Column(TINYINT(1), nullable=False, default=0)
