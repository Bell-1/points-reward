from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pathlib import Path

from app.core.response import BizError, ErrorCode
from app.database import init_db
from app.api import auth, child, admin
from app.config import settings

app = FastAPI(
    title="积分奖励平台",
    description="面向家庭场景的积分激励平台",
    version="1.0.0",
)

# CORS 配置：允许前端开发时跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件目录
STATIC_DIR = Path(__file__).parent / "static"

# 静态文件（上传的图片）
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
# 静态文件（CSS/JS）
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ==================== 统一异常处理 ====================

@app.exception_handler(BizError)
async def biz_error_handler(request: Request, exc: BizError):
    return JSONResponse(
        status_code=200,
        content={"code": exc.code, "msg": exc.msg},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = ".".join(str(l) for l in err.get("loc", []))
        errors.append(f"{loc}: {err.get('msg', '')}")
    return JSONResponse(
        status_code=200,
        content={"code": ErrorCode.VALIDATION_ERROR, "msg": "参数校验失败: " + "; ".join(errors)},
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={"code": ErrorCode.GENERAL_ERROR, "msg": f"服务器内部错误: {str(exc)}"},
    )


# ==================== 路由注册 ====================

app.include_router(auth.router)
app.include_router(child.router)
app.include_router(admin.router)


# ==================== 启动事件 ====================

@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"code": 0, "data": None, "msg": "积分奖励平台 API 运行中"}


# ==================== 前端页面路由 ====================

@app.get("/child/{page}")
async def child_page(page: str):
    """孩子端页面路由"""
    if not page.endswith(".html"):
        page += ".html"
    file = STATIC_DIR / "child" / page
    if file.exists():
        return FileResponse(str(file))
    return JSONResponse(status_code=404, content={"code": -1, "msg": "页面不存在"})


@app.get("/admin/{page}")
async def admin_page(page: str):
    """家长端页面路由"""
    if not page.endswith(".html"):
        page += ".html"
    file = STATIC_DIR / "admin" / page
    if file.exists():
        return FileResponse(str(file))
    return JSONResponse(status_code=404, content={"code": -1, "msg": "页面不存在"})
