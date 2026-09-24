from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

# SQLite 需要 check_same_thread=False
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# SQLite 启用外键约束
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建所有表并初始化默认数据"""
    from app.models import user, task, product, point_record  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # 初始化默认管理员和孩子账户
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        # 默认管理员账户
        admin = db.query(User).filter(User.role == UserRole.admin).first()
        if not admin:
            admin = User(
                nickname="admin",
                role=UserRole.admin,
                password_hash=get_password_hash("admin123"),
            )
            db.add(admin)
            db.commit()

        # 默认孩子账户
        child = db.query(User).filter(
            User.role == UserRole.child,
            User.nickname == "贝希芮",
            User.is_deleted == False,
        ).first()
        if not child:
            child = User(
                nickname="贝希芮",
                role=UserRole.child,
                pin="1234",
                avatar="👧",
            )
            db.add(child)
            db.commit()

        # ==================== 初始任务数据 ====================
        from app.models.task import Task, TaskType

        # 仅当没有任何任务时才创建
        if db.query(Task).count() == 0:
            initial_tasks = [
                # 日常任务（daily）
                ("早起自己穿衣服", TaskType.daily, 2, "👕", 1),
                ("乖乖吃早餐", TaskType.daily, 1, "🍞", 2),
                ("乖乖吃午餐", TaskType.daily, 1, "🍚", 3),
                ("乖乖吃晚餐", TaskType.daily, 1, "🍲", 4),
                ("自己刷牙洗脸", TaskType.daily, 2, "🪥", 5),
                ("按时上床睡觉", TaskType.daily, 2, "🛏", 6),
                ("收拾自己的玩具", TaskType.daily, 3, "🧸", 7),
                ("自己背书包上学", TaskType.daily, 2, "🎒", 8),
                ("认真完成幼儿园作业", TaskType.daily, 3, "✏️", 9),
                ("帮妈妈摆碗筷", TaskType.daily, 1, "🍽", 10),

                # 周任务（weekly）
                ("每周整理一次自己的书桌", TaskType.weekly, 5, "📚", 1),
                ("帮忙打扫一次房间", TaskType.weekly, 8, "🧹", 2),
                ("周末帮爸爸妈妈洗车", TaskType.weekly, 10, "🚗", 3),
                ("每周读3本绘本", TaskType.weekly, 5, "📖", 4),
                ("学会一首新儿歌并表演", TaskType.weekly, 5, "🎵", 5),
                ("一周每天按时完成日常任务", TaskType.weekly, 15, "🏆", 6),

                # 月度任务（monthly）
                ("月度全勤（不迟到不早退）", TaskType.monthly, 20, "📅", 1),
                ("学会自己系鞋带", TaskType.monthly, 15, "👟", 2),
                ("学会写自己的名字", TaskType.monthly, 15, "✍️", 3),
                ("每月坚持读10本绘本", TaskType.monthly, 20, "📚", 4),
                ("帮妈妈做一次简单的烘焙", TaskType.monthly, 15, "🧁", 5),
                ("学会一项新生活技能（如折衣服）", TaskType.monthly, 20, "👕", 6),
                ("连续一个月按时睡觉", TaskType.monthly, 30, "🌙", 7),
                ("月度表现优秀（家长综合评定）", TaskType.monthly, 50, "⭐", 8),
            ]

            for name, ttype, points, icon, order in initial_tasks:
                db.add(Task(
                    task_name=name,
                    task_type=ttype,
                    reward_points=points,
                    icon=icon,
                    is_active=True,
                    sort_order=order,
                ))
            db.commit()

        # ==================== 初始商品数据 ====================
        from app.models.product import Product, ProductStatus

        # 仅当没有任何商品时才创建
        if db.query(Product).count() == 0:
            initial_products = [
                ("小贴纸", 3, 50, "🎀", 1),
                ("棒棒糖", 5, 30, "🍭", 2),
                ("小橡皮擦", 3, 40, "🔸", 3),
                ("彩色铅笔套装", 10, 20, "🖍", 4),
                ("小拼图", 15, 15, "🧩", 5),
                ("儿童绘本", 20, 10, "📕", 6),
                ("小积木套装", 30, 10, "🧱", 7),
                ("毛绒玩具", 35, 8, "🧸", 8),
                ("儿童水彩笔", 8, 25, "🖌", 9),
                ("卡通文具盒", 15, 15, "✏️", 10),
                ("小手工作品套装", 25, 10, "🎨", 11),
                ("周末动物园门票", 50, 5, "🦁", 12),
                ("周末游乐园之旅", 80, 3, "🎡", 13),
                ("一本喜欢的故事书", 25, 10, "📖", 14),
                ("一套乐高积木", 100, 3, "🧩", 15),
            ]

            for name, points, stock, icon, order in initial_products:
                db.add(Product(
                    product_name=name,
                    required_points=points,
                    stock=stock,
                    status=ProductStatus.on_shelf,
                    sort_order=order,
                    image_url=None,
                ))
            db.commit()
    finally:
        db.close()
