"""任务周期工具：根据 taskType 计算 period_key，判断当前周期范围"""
from datetime import date, datetime, timedelta


def get_period_key(task_type: str, dt: datetime | None = None) -> str:
    """根据任务类型返回当前周期的 period_key"""
    d = dt or datetime.now()
    if task_type == "daily":
        return d.strftime("%Y-%m-%d")
    elif task_type == "weekly":
        iso_year, iso_week, _ = d.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    elif task_type == "monthly":
        return d.strftime("%Y-%m")
    elif task_type == "once":
        return "once"
    else:
        raise ValueError(f"Unknown task_type: {task_type}")


def get_date_range_for_range(date_range: str) -> tuple[datetime, datetime]:
    """根据 dateRange 参数 (7d/30d/90d) 返回 (start, end) 时间范围"""
    now = datetime.now()
    days = {"7d": 7, "30d": 30, "90d": 90}.get(date_range, 7)
    start = now - timedelta(days=days)
    return start, now
