"""
FastAPI 应用主入口

项目定位：日语字幕学习分析工具，而不是普通翻译工具。
前端只需要调用 /analyze，一次获得：
1. 面向学习者的自然翻译
2. 句式/语法拆分
3. 重点单词、JLPT 等级、读音和语气说明

当前分析逻辑完全依靠大模型生成，旧版本地语法规则库和单词库仅作为历史兼容文件保留。
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.dependencies import init_services
from app.api.routes import router
from app.middleware import LoggingMiddleware
from app.logging_config import setup_logging

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化服务
    logger.info("初始化服务...")
    init_services()
    logger.info("服务初始化完成")

    yield

    # 关闭时清理资源
    logger.info("应用关闭，清理资源...")


# 创建 FastAPI 应用
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于大模型的日语字幕学习分析 API，提供翻译、句式拆分和重点单词说明",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 添加日志中间件
if settings.DEBUG:
    app.add_middleware(LoggingMiddleware)

# 注册路由
app.include_router(router)


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }
