from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.core.security import decode_access_token
from app.core.response import BizError, ErrorCode

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not creds:
        raise BizError("未登录", code=ErrorCode.UNAUTHORIZED)
    payload = decode_access_token(creds.credentials)
    if not payload:
        raise BizError("Token 无效或已过期", code=ErrorCode.UNAUTHORIZED)

    user_id = payload.get("sub")
    role = payload.get("role")
    if not user_id or not role:
        raise BizError("Token 无效", code=ErrorCode.UNAUTHORIZED)

    user = db.query(User).filter(User.id == int(user_id), User.is_deleted == False).first()
    if not user:
        raise BizError("用户不存在", code=ErrorCode.UNAUTHORIZED)

    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.admin:
        raise BizError("无权限", code=ErrorCode.FORBIDDEN)
    return user


def get_current_child(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.child:
        raise BizError("无权限", code=ErrorCode.FORBIDDEN)
    return user
