from sqlalchemy import Column, String, Integer, Text, DECIMAL
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from app.models.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    parent_id = Column(INTEGER(unsigned=True), nullable=True, comment="父分类ID，NULL为一级")
    name = Column(String(50), nullable=False)
    icon_url = Column(String(500), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    merchant_id = Column(BIGINT(unsigned=True), nullable=False)
    category_id = Column(INTEGER(unsigned=True), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True, comment="商品详情（富文本）")
    cover_image = Column(String(500), nullable=False, comment="主图URL")
    min_points = Column(INTEGER(unsigned=True), nullable=False, comment="最低积分（列表展示用）")
    cash_supplement = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    tags = Column(String(200), nullable=True, comment="逗号分隔：精选,爆品,新品")
    brand = Column(String(100), nullable=True)
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="on_sale/off_shelf/pending",
    )
    total_sales = Column(INTEGER(unsigned=True), nullable=False, default=0, comment="总销量")
    review_count = Column(INTEGER(unsigned=True), nullable=False, default=0)
    good_review_rate = Column(DECIMAL(5, 2), nullable=False, default=100.00, comment="好评率")
    is_self_operated = Column(TINYINT(1), nullable=False, default=0, comment="是否自营（甄选）")


class ProductSku(Base, TimestampMixin):
    __tablename__ = "product_skus"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    product_id = Column(BIGINT(unsigned=True), nullable=False)
    sku_name = Column(String(200), nullable=False, comment="规格描述，如：红色/XL")
    points_price = Column(INTEGER(unsigned=True), nullable=False, comment="该规格积分价")
    cash_supplement = Column(DECIMAL(10, 2), nullable=False, default=0.00)


class ProductImage(Base, TimestampMixin):
    __tablename__ = "product_images"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    product_id = Column(BIGINT(unsigned=True), nullable=False)
    image_url = Column(String(500), nullable=False)
    image_type = Column(String(20), nullable=False, default="gallery", comment="gallery/detail")
    sort_order = Column(Integer, nullable=False, default=0)
