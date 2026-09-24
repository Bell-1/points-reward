import enum
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProductStatus(str, enum.Enum):
    on_shelf = "on_shelf"
    off_shelf = "off_shelf"


class RedemptionStatus(str, enum.Enum):
    pending = "pending"      # 待审核
    approved = "approved"    # 已通过
    rejected = "rejected"    # 已驳回


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(50), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    required_points: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[ProductStatus] = mapped_column(Enum(ProductStatus), nullable=False, default=ProductStatus.on_shelf)
    require_review: Mapped[bool] = mapped_column(default=True, nullable=False)  # 是否需要审核
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class RedemptionRecord(Base):
    __tablename__ = "redemption_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    points_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_after: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[RedemptionStatus] = mapped_column(Enum(RedemptionStatus), nullable=False, default=RedemptionStatus.pending)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    redeemed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
