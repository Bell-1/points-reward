import enum
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RecordType(str, enum.Enum):
    earning = "earning"
    spending = "spending"


class SourceType(str, enum.Enum):
    task = "task"
    manual_add = "manual_add"
    manual_deduct = "manual_deduct"
    exchange = "exchange"


class PointRecord(Base):
    __tablename__ = "point_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    record_type: Mapped[RecordType] = mapped_column(Enum(RecordType), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # 正数获取，负数消耗
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    operator_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
