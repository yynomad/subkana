"""
应用配置管理

使用 pydantic-settings 从环境变量加载配置
支持开发、生产环境区分
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "Japanese Subtitle Learning Analysis API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, production, testing
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]  # 开发环境允许所有源
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 缓存配置
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 缓存生存时间（秒），默认 5 分钟
    CACHE_MAX_SIZE: int = 1000  # 最大缓存条目数
    CACHE_NAMESPACE_LOCAL: str = "local_analysis"
    CACHE_NAMESPACE_AI: str = "ai_analysis"

    # 大模型配置（OpenAI 兼容 Chat Completions 接口）
    LLM_API_KEY: str | None = None
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TIMEOUT: int = 60
    LLM_TEMPERATURE: float = 0.2

    # 旧版本地规则/词库配置（保留文件与配置项，便于历史数据迁移）
    GRAMMAR_RULES_FILE: str = "data/grammar_rules_complete.json"
    VOCABULARY_LEVELS_FILE: str = "data/vocabulary_levels.json"
    MECAB_DICT_TYPE: str = "ipadic"
    MECAB_RC_PATH: str = "/etc/mecabrc"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例（使用缓存）
    
    Returns:
        Settings 实例
    """
    return Settings()

