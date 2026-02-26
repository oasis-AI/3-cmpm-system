from sqlalchemy import Column, String, Integer, DECIMAL
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from app.models.base import Base, TimestampMixin


class PointsRule(Base, TimestampMixin):
    __tablename__ = "points_rules"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    rule_type = Column(
        String(30),
        nullable=False,
        comment="register / recharge_package",
    )
    name = Column(String(100), nullable=False, comment="规则名称")
    points_amount = Column(INTEGER(unsigned=True), nullable=False)
    cash_price = Column(DECIMAL(10, 2), nullable=True, comment="充值套餐现金价（Demo均为0）")
    is_active = Column(TINYINT(1), nullable=False, default=1)


class PointsRecord(Base, TimestampMixin):
    __tablename__ = "points_records"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(BIGINT(unsigned=True), nullable=False)
    type = Column(
        String(30),
        nullable=False,
        comment="register/recharge/exchange/refund/phone_recharge/flow_recharge/manual_add/manual_deduct",
    )
    amount = Column(Integer, nullable=False, comment="变化量（正=增加，负=减少）")
    balance_after = Column(INTEGER(unsigned=True), nullable=False, comment="操作后余额")
    description = Column(String(200), nullable=True)
    ref_id = Column(BIGINT(unsigned=True), nullable=True, comment="关联ID（order_id等）")
    operator_id = Column(BIGINT(unsigned=True), nullable=True, comment="操作人（管理员）ID")
