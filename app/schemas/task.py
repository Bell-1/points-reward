from pydantic import BaseModel, Field
from typing import List
from app.schemas.common import CamelModel


class TaskCreate(BaseModel):
    taskName: str = Field(min_length=2, max_length=30)
    taskType: str = Field(pattern="^(daily|weekly|monthly|once)$")
    rewardPoints: int = Field(ge=1, le=1000)
    icon: str | None = None
    isActive: bool = True
    sortOrder: int = 0


class TaskUpdate(BaseModel):
    taskName: str | None = Field(default=None, min_length=2, max_length=30)
    taskType: str | None = Field(default=None, pattern="^(daily|weekly|monthly|once)$")
    rewardPoints: int | None = Field(default=None, ge=1, le=1000)
    icon: str | None = None
    isActive: bool | None = None
    sortOrder: int | None = None


class TaskResponse(CamelModel):
    id: int
    taskName: str
    taskType: str
    rewardPoints: int
    icon: str | None = None
    isActive: bool
    sortOrder: int


class ChildTaskResponse(CamelModel):
    """孩子端任务列表项，包含完成状态"""
    id: int
    taskName: str
    taskType: str
    rewardPoints: int
    icon: str | None = None
    isCompleted: bool
    completionStatus: str | None = None  # pending / approved / rejected / None
    completedAt: str | None = None


class TaskCompleteResponse(CamelModel):
    taskId: int
    taskName: str
    pointsEarned: int
    currentBalance: int


class TaskProgressItem(CamelModel):
    id: int
    taskName: str
    taskType: str
    rewardPoints: int
    icon: str | None = None
    isCompleted: bool
    completionStatus: str | None = None
    completedAt: str | None = None


class TaskProgressResponse(CamelModel):
    taskType: str
    totalCount: int
    completedCount: int
    completionRate: float
    tasks: list[TaskProgressItem]


class ReviewRequest(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")
    comment: str | None = Field(default=None, max_length=200)


class PendingReviewItem(CamelModel):
    """待审核/已审核任务完成记录"""
    completionId: int
    childId: int
    childName: str
    taskId: int
    taskName: str
    taskType: str
    rewardPoints: int
    icon: str | None = None
    status: str
    completedAt: str
    reviewedAt: str | None = None
    reviewerName: str | None = None
    reviewComment: str | None = None


class TaskOrderItem(CamelModel):
    id: int
    sortOrder: int


class TaskReorderRequest(BaseModel):
    taskOrders: List[TaskOrderItem]
