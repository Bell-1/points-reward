from pydantic import BaseModel
from app.schemas.common import CamelModel


class PointRecordResponse(CamelModel):
    id: int
    recordType: str
    sourceType: str
    sourceName: str
    amount: int
    balanceAfter: int
    operatorId: int | None = None
    remark: str | None = None
    createdAt: str


class PointRecordDetailResponse(CamelModel):
    """家长端积分操作明细"""
    id: int
    recordType: str
    sourceType: str
    sourceName: str
    amount: int
    balanceAfter: int
    operatorId: int | None = None
    operatorName: str | None = None
    remark: str | None = None
    createdAt: str


class BalanceResponse(BaseModel):
    balance: int
