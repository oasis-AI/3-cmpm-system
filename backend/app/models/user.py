from sqlalchemy import Column, BigInteger, String, Integer, Enum, Text
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    phone = Column(String(11), unique=True, nullable=False, comment="手机号（账号）")
    email = Column(String(100), unique=True, nullable=True, comment="邮箱（可选）")
    nickname = Column(String(50), nullable=False, comment="昵称")
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum("user", "merchant", "admin"),
        nullable=False,
        default="user",
        comment="角色",
    )
    points_balance = Column(Integer, nullable=False, default=0, comment="积分余额（冗余）")
    avatar_url = Column(String(500), nullable=True)
    is_banned = Column(TINYINT(1), nullable=False, default=0, comment="是否封禁")
