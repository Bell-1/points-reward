from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应格式"""
    code: int = 0
    data: T | None = None
    msg: str = "success"


class ErrorResponse(BaseModel):
    code: int
    msg: str


# 错误码常量
class ErrorCode:
    SUCCESS = 0
    GENERAL_ERROR = -1
    VALIDATION_ERROR = -2
    UNAUTHORIZED = -3
    FORBIDDEN = -4
    BUSINESS_ERROR = -10


def success(data: Any = None, msg: str = "success") -> dict:
    return {"code": ErrorCode.SUCCESS, "data": data, "msg": msg}


def error(code: int = ErrorCode.GENERAL_ERROR, msg: str = "error") -> dict:
    return {"code": code, "msg": msg}


class BizError(Exception):
    """业务异常，用于在 service 层抛出并由全局异常处理捕获"""

    def __init__(self, msg: str, code: int = ErrorCode.BUSINESS_ERROR):
        self.msg = msg
        self.code = code
        super().__init__(msg)
