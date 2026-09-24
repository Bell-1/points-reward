from pydantic import BaseModel, Field
from app.schemas.common import CamelModel


class ProductCreate(BaseModel):
    productName: str = Field(min_length=2, max_length=50)
    requiredPoints: int = Field(ge=1)
    stock: int = Field(ge=0)
    status: str = Field(default="on_shelf", pattern="^(on_shelf|off_shelf)$")
    imageUrl: str | None = None
    sortOrder: int = 0
    requireReview: bool = True  # 是否需要审核，默认需要


class ProductUpdate(BaseModel):
    productName: str | None = Field(default=None, min_length=2, max_length=50)
    requiredPoints: int | None = Field(default=None, ge=1)
    stock: int | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, pattern="^(on_shelf|off_shelf)$")
    imageUrl: str | None = None
    sortOrder: int | None = None
    requireReview: bool | None = None  # 是否需要审核


class ProductResponse(CamelModel):
    id: int
    productName: str
    imageUrl: str | None = None
    requiredPoints: int
    stock: int
    status: str
    sortOrder: int
    requireReview: bool


class ChildProductResponse(CamelModel):
    """孩子端商品列表项"""
    id: int
    productName: str
    imageUrl: str | None = None
    requiredPoints: int
    stock: int
    isSoldOut: bool
    requireReview: bool  # 是否需要审核


class RedeemResponse(CamelModel):
    productId: int
    productName: str
    pointsCost: int
    currentBalance: int
    stockAfter: int
    status: str  # pending/approved/rejected


class RedemptionRecordResponse(CamelModel):
    """兑换记录响应（家长端）"""
    id: int
    childId: int
    childName: str
    productId: int
    productName: str
    pointsCost: int
    stockAfter: int
    status: str
    redeemedAt: str
    reviewedBy: int | None = None
    reviewedAt: str | None = None


class ReviewRedemptionRequest(CamelModel):
    """审核兑换请求"""
    approved: bool  # True=通过，False=驳回


class UploadImageResponse(CamelModel):
    url: str
