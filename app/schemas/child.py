from pydantic import BaseModel, Field
from app.schemas.common import CamelModel


class ChildCreate(BaseModel):
    nickname: str = Field(min_length=1, max_length=20)
    age: int | None = Field(default=None, ge=3, le=18)
    avatar: str | None = None
    pin: str = Field(min_length=4, max_length=8)


class ChildUpdate(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=20)
    age: int | None = Field(default=None, ge=3, le=18)
    avatar: str | None = None
    pin: str | None = Field(default=None, min_length=4, max_length=8)


class ChildResponse(CamelModel):
    id: int
    nickname: str
    age: int | None = None
    avatar: str | None = None
    balance: int


class AdjustPointsRequest(BaseModel):
    adjustType: str = Field(pattern="^(add|subtract)$")
    amount: int = Field(ge=1)
    reason: str = Field(min_length=1, max_length=100)


class AdjustPointsResponse(CamelModel):
    childId: int
    newBalance: int
    adjustAmount: int
    adjustType: str
