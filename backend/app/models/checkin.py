from sqlalchemy import Column, Integer, Date
from sqlalchemy.dialects.mysql import BIGINT
from app.models.base import Base, TimestampMixin


class CheckIn(Base, TimestampMixin):
    __tablename__ = "checkins"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    user_id = Column(BIGINT(unsigned=True), nullable=False, index=True)
    check_date = Column(Date, nullable=False, comment="签到日期")
    points_earned = Column(Integer, nullable=False, default=10, comment="本次签到获得积分")
    streak_days = Column(Integer, nullable=False, default=1, comment="连续签到天数")
