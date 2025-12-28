"""
日志配置
"""

import logging
import sys
from app.config import get_settings


def setup_logging():
    """配置日志系统"""
    settings = get_settings()
    
    # 配置日志格式
    log_format = settings.LOG_FORMAT
    
    # 配置日志级别
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统初始化完成，级别: {settings.LOG_LEVEL}")

