from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from app.models.base import Base, TimestampMixin


class PhoneRechargeOrder(Base, TimestampMixin):
    __tablename__ = "phone_recharge_orders"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(BIGINT(unsigned=True), nullable=False)
    recharge_type = Column(String(10), nullable=False, comment="phone / flow")
    phone_number = Column(String(11), nullable=False, comment="充值手机号")
    package_name = Column(String(100), nullable=False, comment="套餐名称")
    points_cost = Column(INTEGER(unsigned=True), nullable=False, comment="消耗积分")
    status = Column(String(20), nullable=False, default="success", comment="Demo中直接成功")
