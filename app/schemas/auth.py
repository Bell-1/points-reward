from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class ChildLoginRequest(BaseModel):
    childId: int
    pin: str


class TokenResponse(BaseModel):
    token: str
    role: str
    userId: int
    nickname: str


class UserInfoResponse(BaseModel):
    id: int
    nickname: str
    age: int | None = None
    avatar: str | None = None
    role: str
    balance: int
