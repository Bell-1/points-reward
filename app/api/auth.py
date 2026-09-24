from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user
from app.core.response import success, error, BizError, ErrorCode
from app.schemas.auth import LoginRequest, ChildLoginRequest, TokenResponse, UserInfoResponse

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """家长登录"""
    admin = db.query(User).filter(
        User.role == UserRole.admin,
        User.nickname == req.username,
        User.is_deleted == False,
    ).first()
    if not admin or not admin.password_hash:
        return error(ErrorCode.UNAUTHORIZED, "用户名或密码错误")
    if not verify_password(req.password, admin.password_hash):
        return error(ErrorCode.UNAUTHORIZED, "用户名或密码错误")

    token = create_access_token(admin.id, {"role": admin.role.value})
    return success(data=TokenResponse(
        token=token,
        role=admin.role.value,
        userId=admin.id,
        nickname=admin.nickname,
    ).model_dump(by_alias=True))


@router.post("/child-login")
def child_login(req: ChildLoginRequest, db: Session = Depends(get_db)):
    """孩子通过 PIN 码登录"""
    child = db.query(User).filter(
        User.id == req.childId,
        User.role == UserRole.child,
        User.is_deleted == False,
    ).first()
    if not child:
        return error(ErrorCode.UNAUTHORIZED, "孩子账户不存在")
    if not child.pin or child.pin != req.pin:
        return error(ErrorCode.UNAUTHORIZED, "PIN 码错误")

    token = create_access_token(child.id, {"role": child.role.value})
    return success(data=TokenResponse(
        token=token,
        role=child.role.value,
        userId=child.id,
        nickname=child.nickname,
    ).model_dump(by_alias=True))


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return success(data=UserInfoResponse(
        id=user.id,
        nickname=user.nickname,
        age=user.age,
        avatar=user.avatar,
        role=user.role.value,
        balance=user.balance,
    ).model_dump(by_alias=True))


@router.get("/children-list")
def children_list(db: Session = Depends(get_db)):
    """公开接口：获取孩子列表（仅 id 和昵称，用于孩子登录页选择账户）"""
    children = db.query(User).filter(
        User.role == UserRole.child,
        User.is_deleted == False,
    ).order_by(User.id).all()

    return success(data=[
        {"id": c.id, "nickname": c.nickname, "avatar": c.avatar}
        for c in children
    ])
