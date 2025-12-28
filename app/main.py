"""
FastAPI 应用主入口

为什么对前端只暴露一个 /analyze 接口：
1. 简化前端调用：一次请求获取所有信息（句型+词汇等级）
2. 减少网络往返：避免多次请求（tokenize + grammar + vocabulary）
3. 保证数据一致性：所有分析基于同一份形态素分析结果
4. 便于后续扩展：可以在后端统一处理缓存、优化等逻辑

后续扩展方向：
1. 增加 N3/N2/N1 句型：在 grammar_rules.json 中添加新规则即可
2. 支持前端 hover 高亮：span 字段已提供字符位置，前端可直接使用
3. 多句型冲突处理：当前返回所有匹配，可添加优先级或去重逻辑
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.dependencies import init_services
from app.api.routes import router
from app.middleware import LoggingMiddleware
from app.logging_config import setup_logging

# 设置 MeCab 环境变量（macOS Homebrew 兼容性）
if os.name == 'posix':  # Unix-like systems
    possible_mecabrc_paths = [
        '/opt/homebrew/etc/mecabrc',  # macOS Homebrew
        '/usr/local/etc/mecabrc',    # macOS/Homebrew legacy
        '/etc/mecabrc',              # Linux
    ]

    for path in possible_mecabrc_paths:
        if os.path.exists(path):
            os.environ['MECABRC'] = path
            print(f"设置 MECABRC={path}")
            break

# 配置日志
setup_logging()
import logging
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
    description="基于 MeCab 的日语句子分析 API，提供句型结构和单词等级分析",
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



