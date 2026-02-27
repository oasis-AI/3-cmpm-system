from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.mysql import BIGINT
from app.models.base import Base, TimestampMixin


class RefundRequest(Base, TimestampMixin):
    __tablename__ = "refund_requests"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    order_id = Column(BIGINT(unsigned=True), nullable=False, index=True)
    user_id = Column(BIGINT(unsigned=True), nullable=False, index=True)
    reason = Column(String(500), nullable=False, comment="退款原因")
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="pending/approved/rejected",
    )
    admin_note = Column(Text, nullable=True, comment="管理员处理备注")
