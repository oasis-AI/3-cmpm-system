from sqlalchemy import Column, String, DECIMAL, Text, DateTime, Integer
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from app.models.base import Base, TimestampMixin


class Activity(Base, TimestampMixin):
    __tablename__ = "activities"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(
        String(20),
        nullable=False,
        comment="discount/flash_sale/gift/sign_in",
    )
    banner_url = Column(String(500), nullable=True)
    discount_rate = Column(DECIMAL(4, 2), nullable=True, comment="折扣率，0.8=8折")
    quota = Column(INTEGER(unsigned=True), nullable=True, comment="参与限额，NULL不限")
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="draft", comment="draft/active/ended")
    created_by = Column(BIGINT(unsigned=True), nullable=False, comment="创建管理员ID")


class ActivityProduct(Base, TimestampMixin):
    __tablename__ = "activity_products"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    activity_id = Column(INTEGER(unsigned=True), nullable=False)
    product_id = Column(BIGINT(unsigned=True), nullable=False)
    apply_status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="pending/approved/rejected",
    )


class ActivityParticipant(Base, TimestampMixin):
    __tablename__ = "activity_participants"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    activity_id = Column(INTEGER(unsigned=True), nullable=False)
    user_id = Column(BIGINT(unsigned=True), nullable=False)
