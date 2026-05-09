"""
依赖注入

管理全局服务实例
"""

import logging

from app.config import get_settings
from app.core.llm_client import LLMAnalysisClient
from app.core.service import AnalysisService

logger = logging.getLogger(__name__)

# 全局服务实例
_llm_client: LLMAnalysisClient | None = None
_analysis_service: AnalysisService | None = None

# 旧版健康检查字段，保留为 None 表示当前已不再依赖本地规则/词库组件
_tokenizer = None
_grammar_engine = None
_vocabulary_mapper = None


def init_services():
    """初始化所有服务（在应用启动时调用）"""
    global _llm_client, _analysis_service

    settings = get_settings()
    _llm_client = LLMAnalysisClient(
        api_key=settings.LLM_API_KEY,
        model=settings.LLM_MODEL,
        base_url=settings.LLM_BASE_URL,
        timeout=settings.LLM_TIMEOUT,
        temperature=settings.LLM_TEMPERATURE,
    )

    if _llm_client.is_configured:
        _analysis_service = AnalysisService(llm_client=_llm_client)
        logger.info("AnalysisService 初始化成功，当前使用大模型分析: %s", settings.LLM_MODEL)
    else:
        _analysis_service = None
        logger.warning("LLM_API_KEY 未配置，AnalysisService 未创建")


def get_analysis_service() -> AnalysisService:
    """
    获取分析服务实例（依赖注入）

    Returns:
        AnalysisService 实例

    Raises:
        HTTPException: 如果服务未初始化
    """
    from fastapi import HTTPException

    if _analysis_service is None:
        raise HTTPException(
            status_code=500,
            detail="分析服务未正确初始化，请配置 LLM_API_KEY 后重启服务"
        )
    return _analysis_service
