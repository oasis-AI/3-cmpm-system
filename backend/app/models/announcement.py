from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from app.models.base import Base, TimestampMixin


class Announcement(Base, TimestampMixin):
    __tablename__ = "announcements"

    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_pinned = Column(TINYINT(1), nullable=False, default=0)
    published_at = Column(DateTime, nullable=True, comment="NULL=草稿")
    created_by = Column(BIGINT(unsigned=True), nullable=False)
