from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from app.models.base import Base, TimestampMixin


class Address(Base, TimestampMixin):
    __tablename__ = "addresses"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(BIGINT(unsigned=True), nullable=False)
    receiver_name = Column(String(50), nullable=False)
    receiver_phone = Column(String(11), nullable=False)
    province = Column(String(20), nullable=False)
    city = Column(String(20), nullable=False)
    district = Column(String(20), nullable=False)
    detail = Column(String(200), nullable=False)
    is_default = Column(INTEGER(unsigned=True), nullable=False, default=0)
