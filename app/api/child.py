from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User, UserRole
from app.models.task import Task, TaskCompletion, TaskType
from app.models.product import Product, ProductStatus, RedemptionRecord, RedemptionStatus
from app.models.point_record import PointRecord, RecordType, SourceType
from app.core.deps import get_current_child
from app.core.response import success, error, BizError, ErrorCode
from app.utils.period import get_period_key
from app.schemas.task import ChildTaskResponse, TaskCompleteResponse, TaskProgressResponse, TaskProgressItem
from app.models.task import CompletionStatus
from app.schemas.product import ChildProductResponse, RedeemResponse
from app.schemas.point import PointRecordResponse, BalanceResponse
from app.schemas.common import PageResult

router = APIRouter(prefix="/api/child", tags=["前台-孩子端"])


@router.get("/points/balance")
def get_balance(user: User = Depends(get_current_child)):
    """获取当前孩子的积分余额"""
    return success(data=BalanceResponse(balance=user.balance).model_dump(by_alias=True))


@router.get("/tasks")
def get_tasks(
    taskType: str | None = Query(default=None, pattern="^(daily|weekly|monthly|once)$"),
    user: User = Depends(get_current_child),
    db: Session = Depends(get_db),
):
    """获取任务列表，返回当前周期任务及完成状态"""
    query = db.query(Task).filter(Task.is_active == True, Task.is_deleted == False)
    if taskType:
        query = query.filter(Task.task_type == TaskType(taskType))
    tasks = query.order_by(Task.sort_order, Task.id).all()

    result = []
    for task in tasks:
        period_key = get_period_key(task.task_type.value)
        completion = db.query(TaskCompletion).filter(
            TaskCompletion.user_id == user.id,
            TaskCompletion.task_id == task.id,
            TaskCompletion.period_key == period_key,
        ).first()

        # 确定完成状态
        completion_status = completion.status.value if completion else None
        # once 任务：pending 算完成（已提交但不能重复）；approved 不算（可重新提交）
        # 其他周期任务：approved/pending 都算完成（周期结束后才会重置）
        if task.task_type == TaskType.once:
            is_completed = completion is not None and completion.status == CompletionStatus.pending
        else:
            is_completed = completion is not None and completion.status != CompletionStatus.rejected

        result.append(ChildTaskResponse(
            id=task.id,
            taskName=task.task_name,
            taskType=task.task_type.value,
            rewardPoints=task.reward_points,
            icon=task.icon,
            isCompleted=is_completed,
            completionStatus=completion_status,
            completedAt=completion.completed_at.strftime("%Y-%m-%d %H:%M") if completion else None,
        ).model_dump(by_alias=True))

    return success(data=result)


@router.post("/tasks/{taskId}/complete")
def complete_task(taskId: int, user: User = Depends(get_current_child), db: Session = Depends(get_db)):
    """提交任务完成，状态为 pending，不发放积分，等待家长审核"""
    task = db.query(Task).filter(Task.id == taskId, Task.is_deleted == False).first()
    if not task:
        return error(ErrorCode.BUSINESS_ERROR, "任务不存在")
    if not task.is_active:
        return error(ErrorCode.BUSINESS_ERROR, "任务已下架")

    period_key = get_period_key(task.task_type.value)
    existing = db.query(TaskCompletion).filter(
        TaskCompletion.user_id == user.id,
        TaskCompletion.task_id == taskId,
        TaskCompletion.period_key == period_key,
    ).first()

    # once 任务可以无限次完成：approved 后允许重新提交
    if task.task_type == TaskType.once and existing and existing.status == CompletionStatus.approved:
        # 重置为 pending，允许再次提交
        existing.status = CompletionStatus.pending
        existing.reviewed_by = None
        existing.reviewed_at = None
        existing.review_comment = None
        existing.completed_at = datetime.now(timezone.utc)
        db.commit()
        return success(data=TaskCompleteResponse(
            taskId=taskId,
            taskName=task.task_name,
            pointsEarned=0,
            currentBalance=user.balance,
        ).model_dump(by_alias=True), msg="任务已提交，等待家长审核")

    if existing and existing.status in (CompletionStatus.pending, CompletionStatus.approved):
        return error(ErrorCode.BUSINESS_ERROR, "该任务已提交，等待审核或已通过")

    try:
        if existing and existing.status == CompletionStatus.rejected:
            # 驳回后重新提交：重置为 pending
            existing.status = CompletionStatus.pending
            existing.reviewed_by = None
            existing.reviewed_at = None
            existing.review_comment = None
            existing.completed_at = datetime.now(timezone.utc)
        else:
            # 新建完成记录（pending 状态，不发放积分）
            completion = TaskCompletion(
                user_id=user.id,
                task_id=taskId,
                period_key=period_key,
                points_earned=task.reward_points,
                status=CompletionStatus.pending,
            )
            db.add(completion)

        db.commit()

        return success(data=TaskCompleteResponse(
            taskId=taskId,
            taskName=task.task_name,
            pointsEarned=0,
            currentBalance=user.balance,
        ).model_dump(by_alias=True), msg="任务已提交，等待家长审核")
    except Exception as e:
        db.rollback()
        return error(ErrorCode.GENERAL_ERROR, f"操作失败: {str(e)}")


@router.get("/tasks/progress")
def get_task_progress(
    taskType: str | None = Query(default=None, pattern="^(daily|weekly|monthly)$"),
    user: User = Depends(get_current_child),
    db: Session = Depends(get_db),
):
    """获取任务进度"""
    query = db.query(Task).filter(Task.is_active == True, Task.is_deleted == False)
    if taskType:
        query = query.filter(Task.task_type == TaskType(taskType))
    else:
        # 默认返回所有类型的进度，但按类型分组返回第一个类型
        pass

    tasks = query.order_by(Task.sort_order, Task.id).all()

    # 按类型分组
    type_groups: dict[str, list[Task]] = {}
    for task in tasks:
        type_groups.setdefault(task.task_type.value, []).append(task)

    # 选择要返回的类型
    target_type = taskType if taskType else "daily"
    if target_type not in type_groups:
        # 如果指定的类型没有任务，返回空结果
        return success(data=TaskProgressResponse(
            taskType=target_type,
            totalCount=0,
            completedCount=0,
            completionRate=0.0,
            tasks=[],
        ).model_dump(by_alias=True))

    group_tasks = type_groups[target_type]
    period_key = get_period_key(target_type)

    items = []
    completed_count = 0
    for task in group_tasks:
        completion = db.query(TaskCompletion).filter(
            TaskCompletion.user_id == user.id,
            TaskCompletion.task_id == task.id,
            TaskCompletion.period_key == period_key,
        ).first()
        # 进度只统计 approved
        completion_status = completion.status.value if completion else None
        is_completed = completion is not None and completion.status == CompletionStatus.approved
        if is_completed:
            completed_count += 1
        items.append(TaskProgressItem(
            id=task.id,
            taskName=task.task_name,
            taskType=task.task_type.value,
            rewardPoints=task.reward_points,
            icon=task.icon,
            isCompleted=is_completed,
            completionStatus=completion_status,
            completedAt=completion.completed_at.strftime("%Y-%m-%d %H:%M") if completion else None,
        ))

    total = len(group_tasks)
    rate = (completed_count / total) if total > 0 else 0.0

    return success(data=TaskProgressResponse(
        taskType=target_type,
        totalCount=total,
        completedCount=completed_count,
        completionRate=round(rate, 4),
        tasks=[item.model_dump(by_alias=True) for item in items],
    ).model_dump(by_alias=True))


@router.get("/products")
def get_products(
    user: User = Depends(get_current_child),
    db: Session = Depends(get_db),
):
    """获取上架商品列表"""
    products = db.query(Product).filter(
        Product.status == ProductStatus.on_shelf,
        Product.is_deleted == False,
    ).order_by(Product.sort_order, Product.id.desc()).all()

    result = []
    for p in products:
        result.append(ChildProductResponse(
            id=p.id,
            productName=p.product_name,
            imageUrl=p.image_url,
            requiredPoints=p.required_points,
            stock=p.stock,
            isSoldOut=p.stock <= 0,
            requireReview=p.require_review,
        ).model_dump(by_alias=True))

    return success(data=result)


@router.post("/products/{productId}/redeem")
def redeem_product(
    productId: int,
    user: User = Depends(get_current_child),
    db: Session = Depends(get_db),
):
    """兑换商品：需要审核时预扣积分待审核，无需审核直接兑换"""
    product = db.query(Product).filter(
        Product.id == productId,
        Product.is_deleted == False,
    ).with_for_update().first()
    if not product:
        return error(ErrorCode.BUSINESS_ERROR, "商品不存在")
    if product.status != ProductStatus.on_shelf:
        return error(ErrorCode.BUSINESS_ERROR, "商品已下架")
    if product.stock <= 0:
        return error(ErrorCode.BUSINESS_ERROR, "商品已售罄")
    if user.balance < product.required_points:
        return error(ErrorCode.BUSINESS_ERROR, f"积分余额不足，当前余额 {user.balance} 积分")

    try:
        # 预扣积分
        user.balance -= product.required_points
        # 扣减库存
        product.stock -= 1

        # 写入兑换记录
        redemption = RedemptionRecord(
            user_id=user.id,
            product_id=productId,
            points_cost=product.required_points,
            stock_after=product.stock,
            status=RedemptionStatus.approved if not product.require_review else RedemptionStatus.pending,
        )
        db.add(redemption)

        # 如果需要审核，先预扣积分但不写入最终的积分流水，等审核通过再写入
        if product.require_review:
            db.commit()
            return success(data=RedeemResponse(
                productId=productId,
                productName=product.product_name,
                pointsCost=product.required_points,
                currentBalance=user.balance,
                stockAfter=product.stock,
                status="pending",
            ).model_dump(by_alias=True), msg="兑换申请已提交，等待家长审核")

        # 无需审核，直接写入积分流水
        record = PointRecord(
            user_id=user.id,
            record_type=RecordType.spending,
            source_type=SourceType.exchange,
            source_name=product.product_name,
            amount=-product.required_points,
            balance_after=user.balance,
        )
        db.add(record)
        db.commit()

        return success(data=RedeemResponse(
            productId=productId,
            productName=product.product_name,
            pointsCost=product.required_points,
            currentBalance=user.balance,
            stockAfter=product.stock,
            status="approved",
        ).model_dump(by_alias=True), msg="兑换成功")
    except Exception as e:
        db.rollback()
        return error(ErrorCode.GENERAL_ERROR, f"兑换失败: {str(e)}")


@router.get("/points/records")
def get_point_records(
    recordType: str | None = Query(default=None, pattern="^(earning|spending)$"),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_child),
    db: Session = Depends(get_db),
):
    """分页获取积分记录"""
    query = db.query(PointRecord).filter(PointRecord.user_id == user.id)
    if recordType:
        query = query.filter(PointRecord.record_type == RecordType(recordType))

    total = query.count()
    records = query.order_by(PointRecord.created_at.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    result = []
    for r in records:
        result.append(PointRecordResponse(
            id=r.id,
            recordType=r.record_type.value,
            sourceType=r.source_type.value,
            sourceName=r.source_name,
            amount=r.amount,
            balanceAfter=r.balance_after,
            operatorId=r.operator_id,
            remark=r.remark,
            createdAt=r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ).model_dump(by_alias=True))

    return success(data=PageResult(
        list=result,
        total=total,
        page=page,
        pageSize=pageSize,
    ).model_dump(by_alias=True))


@router.get("/redemptions")
def get_redemptions(
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_child),
    db: Session = Depends(get_db),
):
    """获取当前孩子的兑换记录"""
    query = db.query(RedemptionRecord).filter(RedemptionRecord.user_id == user.id)
    total = query.count()
    records = query.order_by(RedemptionRecord.redeemed_at.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    result = []
    for r in records:
        product = db.query(Product).filter(Product.id == r.product_id).first()
        result.append({
            "id": r.id,
            "productId": r.product_id,
            "productName": product.product_name if product else "未知商品",
            "pointsCost": r.points_cost,
            "stockAfter": r.stock_after,
            "status": r.status.value,
            "redeemedAt": r.redeemed_at.strftime("%Y-%m-%d %H:%M:%S") if r.redeemed_at else "",
            "reviewedAt": r.reviewed_at.strftime("%Y-%m-%d %H:%M:%S") if r.reviewed_at else None,
        })

    return success(data=PageResult(
        list=result,
        total=total,
        page=page,
        pageSize=pageSize,
    ).model_dump(by_alias=True))
