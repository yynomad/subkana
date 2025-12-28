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
    APP_NAME: str = "Japanese Sentence Analysis API"
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
    
    # 文件路径配置
    GRAMMAR_RULES_FILE: str = "data/grammar_rules.json"
    VOCABULARY_LEVELS_FILE: str = "data/vocabulary_levels.json"
    
    # MeCab 配置
    MECAB_DICT_TYPE: str = "ipadic"  # ipadic, unidic, etc.
    
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

