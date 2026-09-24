from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class CamelModel(BaseModel):
    """启用 camelCase 别名的基类"""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: _to_camel(field_name),
        from_attributes=True,
    )


def _to_camel(snake_str: str) -> str:
    parts = snake_str.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class PageResult(BaseModel, Generic[T]):
    """分页结果"""
    list: list[T]
    total: int
    page: int
    pageSize: int
