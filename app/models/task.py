import enum
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Enum, DateTime, Boolean, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TaskType(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    once = "once"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    task_type: Mapped[TaskType] = mapped_column(Enum(TaskType), nullable=False)
    reward_points: Mapped[int] = mapped_column(Integer, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class CompletionStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class TaskCompletion(Base):
    __tablename__ = "task_completions"
    __table_args__ = (
        UniqueConstraint("user_id", "task_id", "period_key", name="uq_task_completion_period"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    period_key: Mapped[str] = mapped_column(String(20), nullable=False)  # 2026-09-22 / 2026-W38 / 2026-09
    points_earned: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[CompletionStatus] = mapped_column(Enum(CompletionStatus), nullable=False, default=CompletionStatus.pending)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    review_comment: Mapped[str | None] = mapped_column(String(200), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
