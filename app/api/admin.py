import os
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.database import get_db
from app.config import settings
from app.models.user import User, UserRole
from app.models.task import Task, TaskCompletion, TaskType, CompletionStatus
from app.models.product import Product, ProductStatus, RedemptionRecord, RedemptionStatus
from app.models.point_record import PointRecord, RecordType, SourceType
from app.core.deps import get_current_admin
from app.core.response import success, error, BizError, ErrorCode
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, ReviewRequest, PendingReviewItem, TaskReorderRequest
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, UploadImageResponse, RedemptionRecordResponse, ReviewRedemptionRequest
from app.schemas.child import ChildCreate, ChildUpdate, ChildResponse, AdjustPointsRequest, AdjustPointsResponse
from app.schemas.point import PointRecordDetailResponse
from app.schemas.stats import StatsOverviewResponse, StatsTrendResponse, TrendDayItem
from app.schemas.common import PageResult, CamelModel

router = APIRouter(prefix="/api/admin", tags=["后台-家长端"])


# ==================== 任务管理 ====================

@router.get("/tasks")
def list_tasks(
    taskType: str | None = Query(default=None, pattern="^(daily|weekly|monthly|once)$"),
    isActive: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """任务列表"""
    query = db.query(Task).filter(Task.is_deleted == False)
    if taskType:
        query = query.filter(Task.task_type == TaskType(taskType))
    if isActive is not None:
        query = query.filter(Task.is_active == isActive)

    total = query.count()
    tasks = query.order_by(Task.sort_order, Task.id).offset((page - 1) * pageSize).limit(pageSize).all()

    result = [TaskResponse(
        id=t.id,
        taskName=t.task_name,
        taskType=t.task_type.value,
        rewardPoints=t.reward_points,
        icon=t.icon,
        isActive=t.is_active,
        sortOrder=t.sort_order,
    ).model_dump(by_alias=True) for t in tasks]

    return success(data=PageResult(
        list=result, total=total, page=page, pageSize=pageSize,
    ).model_dump(by_alias=True))


@router.post("/tasks")
def create_task(req: TaskCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """创建任务"""
    existing = db.query(Task).filter(Task.task_name == req.taskName, Task.is_deleted == False).first()
    if existing:
        return error(ErrorCode.BUSINESS_ERROR, "任务名称已存在")

    task = Task(
        task_name=req.taskName,
        task_type=TaskType(req.taskType),
        reward_points=req.rewardPoints,
        icon=req.icon,
        is_active=req.isActive,
        sort_order=req.sortOrder,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return success(data=TaskResponse(
            id=task.id, taskName=task.task_name, taskType=task.task_type.value,
            rewardPoints=task.reward_points, icon=task.icon, isActive=task.is_active,
            sortOrder=task.sort_order,
        ).model_dump(by_alias=True), msg="任务创建成功")


@router.put("/tasks/reorder")
def reorder_tasks(
    req: TaskReorderRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """批量更新任务排序"""
    try:
        for item in req.taskOrders:
            task = db.query(Task).filter(Task.id == item.id, Task.is_deleted == False).first()
            if task:
                task.sort_order = item.sortOrder
        db.commit()
        return success(msg="排序已更新")
    except Exception as e:
        db.rollback()
        return error(ErrorCode.GENERAL_ERROR, f"更新排序失败: {str(e)}")


@router.put("/tasks/{taskId}")
def update_task(taskId: int, req: TaskUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """更新任务"""
    task = db.query(Task).filter(Task.id == taskId, Task.is_deleted == False).first()
    if not task:
        return error(ErrorCode.BUSINESS_ERROR, "任务不存在")

    if req.taskName is not None:
        existing = db.query(Task).filter(
            Task.task_name == req.taskName,
            Task.id != taskId,
            Task.is_deleted == False,
        ).first()
        if existing:
            return error(ErrorCode.BUSINESS_ERROR, "任务名称已存在")
        task.task_name = req.taskName

    if req.taskType is not None:
        task.task_type = TaskType(req.taskType)
    if req.rewardPoints is not None:
        task.reward_points = req.rewardPoints
    if req.icon is not None:
        task.icon = req.icon
    if req.isActive is not None:
        task.is_active = req.isActive
    if req.sortOrder is not None:
        task.sort_order = req.sortOrder

    db.commit()
    db.refresh(task)

    return success(data=TaskResponse(
        id=task.id, taskName=task.task_name, taskType=task.task_type.value,
        rewardPoints=task.reward_points, icon=task.icon, isActive=task.is_active,
        sortOrder=task.sort_order,
    ).model_dump(by_alias=True), msg="任务更新成功")


@router.delete("/tasks/{taskId}")
def delete_task(taskId: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """软删除任务"""
    task = db.query(Task).filter(Task.id == taskId, Task.is_deleted == False).first()
    if not task:
        return error(ErrorCode.BUSINESS_ERROR, "任务不存在")

    task.is_deleted = True
    db.commit()
    return success(msg="任务删除成功")


# ==================== 任务审核 ====================

@router.get("/tasks/pending")
def list_pending_reviews(
    childId: int | None = Query(default=None),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取待审核的任务完成记录（仅 pending 状态）"""
    query = db.query(TaskCompletion).filter(
        TaskCompletion.status == CompletionStatus.pending,
    )
    if childId:
        query = query.filter(TaskCompletion.user_id == childId)

    completions = query.order_by(TaskCompletion.completed_at.desc()).all()

    result = []
    for c in completions:
        child = db.query(User).filter(User.id == c.user_id).first()
        task = db.query(Task).filter(Task.id == c.task_id).first()
        if not child or not task:
            continue
        reviewer = db.query(User).filter(User.id == c.reviewed_by).first() if c.reviewed_by else None
        result.append(PendingReviewItem(
            completionId=c.id,
            childId=c.user_id,
            childName=child.nickname,
            taskId=c.task_id,
            taskName=task.task_name,
            taskType=task.task_type.value,
            rewardPoints=c.points_earned,
            icon=task.icon,
            status=c.status.value,
            completedAt=c.completed_at.strftime("%Y-%m-%d %H:%M"),
            reviewedAt=c.reviewed_at.strftime("%Y-%m-%d %H:%M") if c.reviewed_at else None,
            reviewerName=reviewer.nickname if reviewer else None,
            reviewComment=c.review_comment,
        ).model_dump(by_alias=True))

    return success(data=result)


@router.get("/tasks/reviewed")
def list_reviewed(
    childId: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取已审核的任务完成记录（approved + rejected），支持分页和按孩子筛选"""
    query = db.query(TaskCompletion).filter(
        TaskCompletion.status.in_([CompletionStatus.approved, CompletionStatus.rejected]),
    )
    if childId:
        query = query.filter(TaskCompletion.user_id == childId)

    total = query.count()
    completions = query.order_by(TaskCompletion.reviewed_at.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    result = []
    for c in completions:
        child = db.query(User).filter(User.id == c.user_id).first()
        task = db.query(Task).filter(Task.id == c.task_id).first()
        if not child or not task:
            continue
        reviewer = db.query(User).filter(User.id == c.reviewed_by).first() if c.reviewed_by else None
        result.append(PendingReviewItem(
            completionId=c.id,
            childId=c.user_id,
            childName=child.nickname,
            taskId=c.task_id,
            taskName=task.task_name,
            taskType=task.task_type.value,
            rewardPoints=c.points_earned,
            icon=task.icon,
            status=c.status.value,
            completedAt=c.completed_at.strftime("%Y-%m-%d %H:%M"),
            reviewedAt=c.reviewed_at.strftime("%Y-%m-%d %H:%M") if c.reviewed_at else None,
            reviewerName=reviewer.nickname if reviewer else None,
            reviewComment=c.review_comment,
        ).model_dump(by_alias=True))

    return success(data=PageResult(
        list=result, total=total, page=page, pageSize=pageSize,
    ).model_dump(by_alias=True))


@router.post("/tasks/{completion_id}/review")
def review_completion(
    completion_id: int,
    req: ReviewRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """审核任务完成记录：approve 发放积分，reject 不发放"""
    completion = db.query(TaskCompletion).filter(
        TaskCompletion.id == completion_id,
    ).first()
    if not completion:
        return error(ErrorCode.BUSINESS_ERROR, "完成记录不存在")
    if completion.status != CompletionStatus.pending:
        return error(ErrorCode.BUSINESS_ERROR, "该记录已被审核")

    task = db.query(Task).filter(Task.id == completion.task_id).first()
    if not task:
        return error(ErrorCode.BUSINESS_ERROR, "关联任务不存在")

    child = db.query(User).filter(User.id == completion.user_id).first()
    if not child:
        return error(ErrorCode.BUSINESS_ERROR, "孩子账户不存在")

    try:
        now = datetime.now(timezone.utc)
        completion.reviewed_by = admin.id
        completion.reviewed_at = now
        completion.review_comment = req.comment

        if req.action == "approve":
            completion.status = CompletionStatus.approved
            # 此时才发放积分
            child.balance += task.reward_points
            # 写入积分流水
            record = PointRecord(
                user_id=child.id,
                record_type=RecordType.earning,
                source_type=SourceType.task,
                source_name=task.task_name,
                amount=task.reward_points,
                balance_after=child.balance,
            )
            db.add(record)
            db.commit()
            return success(data={
                "completionId": completion_id,
                "status": "approved",
                "newBalance": child.balance,
                "pointsEarned": task.reward_points,
            }, msg="审核通过，积分已发放")
        else:
            completion.status = CompletionStatus.rejected
            db.commit()
            return success(data={
                "completionId": completion_id,
                "status": "rejected",
            }, msg="已驳回")
    except Exception as e:
        db.rollback()
        return error(ErrorCode.GENERAL_ERROR, f"审核失败: {str(e)}")


# ==================== 商品管理 ====================

@router.get("/products")
def list_products(
    status: str | None = Query(default=None, pattern="^(on_shelf|off_shelf)$"),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """商品列表"""
    query = db.query(Product).filter(Product.is_deleted == False)
    if status:
        query = query.filter(Product.status == ProductStatus(status))

    total = query.count()
    products = query.order_by(Product.sort_order, Product.id.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    result = [ProductResponse(
        id=p.id, productName=p.product_name, imageUrl=p.image_url,
        requiredPoints=p.required_points, stock=p.stock,
        status=p.status.value, sortOrder=p.sort_order,
        requireReview=p.require_review,
    ).model_dump(by_alias=True) for p in products]

    return success(data=PageResult(
        list=result, total=total, page=page, pageSize=pageSize,
    ).model_dump(by_alias=True))


@router.post("/products")
def create_product(req: ProductCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """创建商品"""
    product = Product(
        product_name=req.productName,
        image_url=req.imageUrl,
        required_points=req.requiredPoints,
        stock=req.stock,
        status=ProductStatus(req.status),
        sort_order=req.sortOrder,
        require_review=req.requireReview,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    return success(data=ProductResponse(
        id=product.id, productName=product.product_name, imageUrl=product.image_url,
        requiredPoints=product.required_points, stock=product.stock,
        status=product.status.value, sortOrder=product.sort_order,
        requireReview=product.require_review,
    ).model_dump(by_alias=True), msg="商品创建成功")


@router.put("/products/{productId}")
def update_product(productId: int, req: ProductUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """更新商品"""
    product = db.query(Product).filter(Product.id == productId, Product.is_deleted == False).first()
    if not product:
        return error(ErrorCode.BUSINESS_ERROR, "商品不存在")

    if req.productName is not None:
        product.product_name = req.productName
    if req.imageUrl is not None:
        product.image_url = req.imageUrl
    if req.requiredPoints is not None:
        product.required_points = req.requiredPoints
    if req.stock is not None:
        product.stock = req.stock
    if req.status is not None:
        product.status = ProductStatus(req.status)
    if req.sortOrder is not None:
        product.sort_order = req.sortOrder
    if req.requireReview is not None:
        product.require_review = req.requireReview

    db.commit()
    db.refresh(product)

    return success(data=ProductResponse(
        id=product.id, productName=product.product_name, imageUrl=product.image_url,
        requiredPoints=product.required_points, stock=product.stock,
        status=product.status.value, sortOrder=product.sort_order,
        requireReview=product.require_review,
    ).model_dump(by_alias=True), msg="商品更新成功")


@router.delete("/products/{productId}")
def delete_product(productId: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """软删除商品"""
    product = db.query(Product).filter(Product.id == productId, Product.is_deleted == False).first()
    if not product:
        return error(ErrorCode.BUSINESS_ERROR, "商品不存在")

    product.is_deleted = True
    db.commit()
    return success(msg="商品删除成功")


# ==================== 兑换审核管理 ====================

@router.get("/redemptions/pending")
def list_pending_redemptions(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取待审核的兑换记录"""
    records = db.query(RedemptionRecord).filter(
        RedemptionRecord.status == RedemptionStatus.pending
    ).order_by(RedemptionRecord.redeemed_at.desc()).all()

    result = []
    for r in records:
        child = db.query(User).filter(User.id == r.user_id).first()
        product = db.query(Product).filter(Product.id == r.product_id).first()
        result.append(RedemptionRecordResponse(
            id=r.id,
            childId=r.user_id,
            childName=child.nickname if child else "未知",
            productId=r.product_id,
            productName=product.product_name if product else "未知",
            pointsCost=r.points_cost,
            stockAfter=r.stock_after,
            status=r.status.value,
            redeemedAt=r.redeemed_at.isoformat() if r.redeemed_at else "",
            reviewedBy=r.reviewed_by,
            reviewedAt=r.reviewed_at.isoformat() if r.reviewed_at else None,
        ).model_dump(by_alias=True))
    return success(data=result)


@router.get("/redemptions/approved")
def list_approved_redemptions(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取已通过的兑换记录"""
    query = db.query(RedemptionRecord).filter(RedemptionRecord.status == RedemptionStatus.approved)
    total = query.count()
    records = query.order_by(RedemptionRecord.redeemed_at.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    result = []
    for r in records:
        child = db.query(User).filter(User.id == r.user_id).first()
        product = db.query(Product).filter(Product.id == r.product_id).first()
        result.append(RedemptionRecordResponse(
            id=r.id,
            childId=r.user_id,
            childName=child.nickname if child else "未知",
            productId=r.product_id,
            productName=product.product_name if product else "未知",
            pointsCost=r.points_cost,
            stockAfter=r.stock_after,
            status=r.status.value,
            redeemedAt=r.redeemed_at.isoformat() if r.redeemed_at else "",
            reviewedBy=r.reviewed_by,
            reviewedAt=r.reviewed_at.isoformat() if r.reviewed_at else None,
        ).model_dump(by_alias=True))
    return success(data=PageResult(
        list=result,
        total=total,
        page=page,
        pageSize=pageSize,
    ).model_dump(by_alias=True))


@router.post("/redemptions/{redemption_id}/review")
def review_redemption(
    redemption_id: int,
    req: ReviewRedemptionRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """审核兑换申请：批准或驳回"""
    redemption = db.query(RedemptionRecord).filter(
        RedemptionRecord.id == redemption_id
    ).with_for_update().first()
    if not redemption:
        return error(ErrorCode.BUSINESS_ERROR, "兑换记录不存在")
    if redemption.status != RedemptionStatus.pending:
        return error(ErrorCode.BUSINESS_ERROR, "该兑换记录已审核过")

    child = db.query(User).filter(User.id == redemption.user_id).first()
    if not child:
        return error(ErrorCode.BUSINESS_ERROR, "孩子账户不存在")

    if req.approved:
        # 审核通过：写入积分流水（真正扣除）
        record = PointRecord(
            user_id=child.id,
            record_type=RecordType.spending,
            source_type=SourceType.exchange,
            source_name=f"兑换审核通过",
            amount=-redemption.points_cost,
            balance_after=child.balance,
            operator_id=admin.id,
        )
        db.add(record)
        redemption.status = RedemptionStatus.approved
        msg = "兑换审核通过"
    else:
        # 驳回：返还积分、加回库存
        child.balance += redemption.points_cost
        product = db.query(Product).filter(Product.id == redemption.product_id).first()
        if product:
            product.stock += 1
        redemption.status = RedemptionStatus.rejected
        redemption.stock_after = product.stock if product else redemption.stock_after
        msg = "兑换已驳回，积分已返还"

    redemption.reviewed_by = admin.id
    redemption.reviewed_at = datetime.now(timezone.utc)
    db.commit()

    return success(msg=msg)


@router.get("/redemptions/pending/count")
def get_pending_redemption_count(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取待审核兑换数量"""
    count = db.query(RedemptionRecord).filter(
        RedemptionRecord.status == RedemptionStatus.pending
    ).count()
    return success(data={"count": count})


# ==================== 图片上传 ====================

@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin),
):
    """上传商品图片"""
    # 校验文件类型
    allowed_types = {"image/jpeg", "image/png", "image/jpg"}
    if file.content_type not in allowed_types:
        return error(ErrorCode.VALIDATION_ERROR, "仅支持 JPG/PNG 格式")

    # 读取并保存文件（不限制大小）
    content = await file.read()

    # 保存文件
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    url = f"/uploads/{filename}"
    return success(data=UploadImageResponse(url=url).model_dump(by_alias=True))


# ==================== 孩子管理 ====================

@router.get("/children")
def list_children(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """获取所有孩子账户"""
    children = db.query(User).filter(
        User.role == UserRole.child,
        User.is_deleted == False,
    ).order_by(User.id).all()

    result = [ChildResponse(
        id=c.id, nickname=c.nickname, age=c.age, avatar=c.avatar, balance=c.balance,
    ).model_dump(by_alias=True) for c in children]

    return success(data=result)


@router.post("/children")
def create_child(req: ChildCreate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """添加孩子"""
    existing = db.query(User).filter(
        User.nickname == req.nickname,
        User.role == UserRole.child,
        User.is_deleted == False,
    ).first()
    if existing:
        return error(ErrorCode.BUSINESS_ERROR, "该昵称已存在")

    child = User(
        nickname=req.nickname,
        age=req.age,
        avatar=req.avatar,
        role=UserRole.child,
        pin=req.pin,
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    return success(data=ChildResponse(
        id=child.id, nickname=child.nickname, age=child.age, avatar=child.avatar, balance=child.balance,
    ).model_dump(by_alias=True), msg="孩子账户创建成功")


@router.put("/children/{childId}")
def update_child(childId: int, req: ChildUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """更新孩子信息"""
    child = db.query(User).filter(
        User.id == childId,
        User.role == UserRole.child,
        User.is_deleted == False,
    ).first()
    if not child:
        return error(ErrorCode.BUSINESS_ERROR, "孩子账户不存在")

    if req.nickname is not None:
        existing = db.query(User).filter(
            User.nickname == req.nickname,
            User.role == UserRole.child,
            User.id != childId,
            User.is_deleted == False,
        ).first()
        if existing:
            return error(ErrorCode.BUSINESS_ERROR, "该昵称已存在")
        child.nickname = req.nickname

    if req.age is not None:
        child.age = req.age
    if req.avatar is not None:
        child.avatar = req.avatar
    if req.pin is not None:
        child.pin = req.pin

    db.commit()
    db.refresh(child)

    return success(data=ChildResponse(
        id=child.id, nickname=child.nickname, age=child.age, avatar=child.avatar, balance=child.balance,
    ).model_dump(by_alias=True), msg="孩子信息更新成功")


@router.post("/children/{childId}/adjust-points")
def adjust_points(
    childId: int,
    req: AdjustPointsRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """手动调整孩子积分"""
    child = db.query(User).filter(
        User.id == childId,
        User.role == UserRole.child,
        User.is_deleted == False,
    ).first()
    if not child:
        return error(ErrorCode.BUSINESS_ERROR, "孩子账户不存在")

    if req.adjustType == "subtract" and child.balance < req.amount:
        return error(ErrorCode.BUSINESS_ERROR, f"积分余额不足，当前余额 {child.balance} 积分")

    try:
        if req.adjustType == "add":
            child.balance += req.amount
            record_type = RecordType.earning
            source_type = SourceType.manual_add
            amount = req.amount
        else:
            child.balance -= req.amount
            record_type = RecordType.spending
            source_type = SourceType.manual_deduct
            amount = -req.amount

        record = PointRecord(
            user_id=child.id,
            record_type=record_type,
            source_type=source_type,
            source_name="手动调整积分",
            amount=amount,
            balance_after=child.balance,
            operator_id=admin.id,
            remark=req.reason,
        )
        db.add(record)
        db.commit()
        db.refresh(child)

        return success(data=AdjustPointsResponse(
            childId=child.id,
            newBalance=child.balance,
            adjustAmount=req.amount,
            adjustType=req.adjustType,
        ).model_dump(by_alias=True), msg="积分调整成功")
    except Exception as e:
        db.rollback()
        return error(ErrorCode.GENERAL_ERROR, f"调整失败: {str(e)}")


@router.get("/children/{childId}/points/records")
def get_child_point_records(
    childId: int,
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    startDate: str | None = Query(default=None),
    endDate: str | None = Query(default=None),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """查询孩子手动积分操作明细（manual_add + manual_deduct）"""
    child = db.query(User).filter(
        User.id == childId,
        User.role == UserRole.child,
        User.is_deleted == False,
    ).first()
    if not child:
        return error(ErrorCode.BUSINESS_ERROR, "孩子账户不存在")

    query = db.query(PointRecord).filter(
        PointRecord.user_id == childId,
        PointRecord.source_type.in_([SourceType.manual_add, SourceType.manual_deduct, SourceType.exchange]),
    )
    if startDate:
        try:
            sd = datetime.strptime(startDate, "%Y-%m-%d")
            query = query.filter(PointRecord.created_at >= sd)
        except ValueError:
            pass
    if endDate:
        try:
            ed = datetime.strptime(endDate, "%Y-%m-%d")
            ed = ed + timedelta(days=1)
            query = query.filter(PointRecord.created_at < ed)
        except ValueError:
            pass

    total = query.count()
    records = query.order_by(PointRecord.created_at.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    result = []
    for r in records:
        operator = db.query(User).filter(User.id == r.operator_id).first() if r.operator_id else None
        result.append(PointRecordDetailResponse(
            id=r.id,
            recordType=r.record_type.value,
            sourceType=r.source_type.value,
            sourceName=r.source_name,
            amount=r.amount,
            balanceAfter=r.balance_after,
            operatorId=r.operator_id,
            operatorName=operator.nickname if operator else None,
            remark=r.remark,
            createdAt=r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ).model_dump(by_alias=True))

    return success(data=PageResult(
        list=result, total=total, page=page, pageSize=pageSize,
    ).model_dump(by_alias=True))


# ==================== 数据统计 ====================

@router.get("/stats/overview")
def stats_overview(
    dateRange: str = Query(default="7d", pattern="^(7d|30d|90d)$"),
    childId: int | None = Query(default=None),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """统计数据总览"""
    days = {"7d": 7, "30d": 30, "90d": 90}.get(dateRange, 7)
    start = datetime.now(timezone.utc) - timedelta(days=days)

    # 积分记录过滤
    record_query = db.query(PointRecord).filter(PointRecord.created_at >= start)
    if childId:
        record_query = record_query.filter(PointRecord.user_id == childId)

    # 总积分发放
    total_issued = record_query.filter(
        PointRecord.record_type == RecordType.earning,
        PointRecord.amount > 0,
    ).with_entities(func.coalesce(func.sum(PointRecord.amount), 0)).scalar() or 0

    # 总兑换次数
    total_redeem = record_query.filter(
        PointRecord.record_type == RecordType.spending,
        PointRecord.source_type == SourceType.exchange,
    ).count()

    # 活跃孩子数
    active_query = db.query(PointRecord).filter(
        PointRecord.created_at >= start,
        PointRecord.source_type == SourceType.task,
    )
    if childId:
        active_query = active_query.filter(PointRecord.user_id == childId)
    active_child_count = active_query.with_entities(distinct(PointRecord.user_id)).count()

    # 任务完成率
    total_active_tasks = db.query(Task).filter(
        Task.is_active == True,
        Task.is_deleted == False,
    ).count()
    total_children = db.query(User).filter(
        User.role == UserRole.child,
        User.is_deleted == False,
    ).count()

    # 完成数（只统计 approved）
    completion_query = db.query(TaskCompletion).filter(
        TaskCompletion.completed_at >= start,
        TaskCompletion.status == CompletionStatus.approved,
    )
    if childId:
        completion_query = completion_query.filter(TaskCompletion.user_id == childId)
    completed_count = completion_query.count()

    # 应完成数 = 活跃任务数 × 周期数 × 孩子数（简化计算）
    # 周期数 = days / 该周期天数
    daily_periods = days  # 每天一个周期
    weekly_periods = days // 7 + (1 if days % 7 else 0)
    monthly_periods = days // 30 + (1 if days % 30 else 0)

    daily_tasks = db.query(Task).filter(
        Task.is_active == True, Task.is_deleted == False, Task.task_type == TaskType.daily,
    ).count()
    weekly_tasks = db.query(Task).filter(
        Task.is_active == True, Task.is_deleted == False, Task.task_type == TaskType.weekly,
    ).count()
    monthly_tasks = db.query(Task).filter(
        Task.is_active == True, Task.is_deleted == False, Task.task_type == TaskType.monthly,
    ).count()

    children_count = childId and 1 or total_children
    expected = (daily_tasks * daily_periods + weekly_tasks * weekly_periods + monthly_tasks * monthly_periods) * children_count
    completion_rate = round(completed_count / expected, 4) if expected > 0 else 0.0

    # 待审核任务数
    pending_query = db.query(TaskCompletion).filter(
        TaskCompletion.status == CompletionStatus.pending,
    )
    if childId:
        pending_query = pending_query.filter(TaskCompletion.user_id == childId)
    pending_review_count = pending_query.count()

    return success(data=StatsOverviewResponse(
        totalPointsIssued=total_issued,
        totalRedeemCount=total_redeem,
        taskCompletionRate=completion_rate,
        activeChildCount=active_child_count,
        pendingReviewCount=pending_review_count,
    ).model_dump(by_alias=True))


@router.get("/stats/trend")
def stats_trend(
    dateRange: str = Query(default="7d", pattern="^(7d|30d|90d)$"),
    childId: int | None = Query(default=None),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """统计趋势数据"""
    days = {"7d": 7, "30d": 30, "90d": 90}.get(dateRange, 7)
    start = datetime.now() - timedelta(days=days)

    # 获取每日发放积分
    earning_query = db.query(
        func.date(PointRecord.created_at).label("date"),
        func.sum(PointRecord.amount).label("total"),
    ).filter(
        PointRecord.created_at >= start,
        PointRecord.record_type == RecordType.earning,
        PointRecord.amount > 0,
    )
    if childId:
        earning_query = earning_query.filter(PointRecord.user_id == childId)
    earning_data = earning_query.group_by(func.date(PointRecord.created_at)).all()
    earning_map = {row.date: row.total or 0 for row in earning_data}

    # 获取每日兑换积分
    redeem_query = db.query(
        func.date(PointRecord.created_at).label("date"),
        func.abs(func.sum(PointRecord.amount)).label("total"),
    ).filter(
        PointRecord.created_at >= start,
        PointRecord.record_type == RecordType.spending,
        PointRecord.source_type == SourceType.exchange,
    )
    if childId:
        redeem_query = redeem_query.filter(PointRecord.user_id == childId)
    redeem_data = redeem_query.group_by(func.date(PointRecord.created_at)).all()
    redeem_map = {row.date: row.total or 0 for row in redeem_data}

    # 构建每日趋势
    trend = []
    for i in range(days):
        d = (datetime.now() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        # SQLite 返回的 date 是字符串
        issued = earning_map.get(d, 0)
        redeemed = redeem_map.get(d, 0)
        trend.append(TrendDayItem(
            date=d,
            pointsIssued=issued,
            pointsRedeemed=redeemed,
        ).model_dump(by_alias=True))

    return success(data=StatsTrendResponse(
        dateRange=dateRange,
        trend=trend,
    ).model_dump(by_alias=True))
