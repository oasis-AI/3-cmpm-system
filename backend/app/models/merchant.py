from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.mysql import BIGINT
from app.models.base import Base, TimestampMixin


class Merchant(Base, TimestampMixin):
    __tablename__ = "merchants"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(BIGINT(unsigned=True), nullable=False, comment="关联 users.id")
    merchant_name = Column(String(100), nullable=False, comment="商户名称")
    contact_name = Column(String(50), nullable=False, comment="联系人")
    contact_phone = Column(String(11), nullable=False)
    business_license = Column(String(500), nullable=True, comment="营业执照URL")
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="pending/approved/rejected",
    )
    reject_reason = Column(String(500), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    reviewed_by = Column(BIGINT(unsigned=True), nullable=True, comment="审核管理员 user_id")
