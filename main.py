"""
应用启动入口

使用 uvicorn 启动 FastAPI 应用
"""

import os
import uvicorn
from app.config import get_settings

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

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
