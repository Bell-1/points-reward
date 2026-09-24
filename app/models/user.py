import enum
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    child = "child"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(20), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.child)
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)  # admin 需要密码，child 用 PIN
    pin: Mapped[str | None] = mapped_column(String(10), nullable=True)  # 孩子登录 PIN
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
