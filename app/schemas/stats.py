from pydantic import BaseModel
from app.schemas.common import CamelModel


class StatsOverviewResponse(CamelModel):
    totalPointsIssued: int
    totalRedeemCount: int
    taskCompletionRate: float
    activeChildCount: int
    pendingReviewCount: int = 0


class TrendDayItem(CamelModel):
    date: str
    pointsIssued: int
    pointsRedeemed: int


class StatsTrendResponse(CamelModel):
    dateRange: str
    trend: list[TrendDayItem]
