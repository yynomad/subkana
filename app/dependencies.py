"""
依赖注入

管理全局服务实例
"""

import logging

from app.config import get_settings
from app.core.cache import MemoryCache
from app.core.llm_client import LLMAnalysisClient
from app.core.service import AnalysisService

logger = logging.getLogger(__name__)

# 全局服务实例
_llm_client: LLMAnalysisClient | None = None
_analysis_service: AnalysisService | None = None
_tokenizer = None
_grammar_engine = None
_vocabulary_mapper = None

# 缓存实例（供路由查看/管理）
_cache_local: MemoryCache | None = None
_cache_ai: MemoryCache | None = None


def init_services():
    """初始化所有服务（在应用启动时调用）"""
    global _llm_client, _analysis_service, _tokenizer, _grammar_engine, _vocabulary_mapper
    global _cache_local, _cache_ai

    settings = get_settings()

    # 本地分析组件
    try:
        from app.core.tokenizer import MeCabTokenizer
        _tokenizer = MeCabTokenizer(
            dict_type=settings.MECAB_DICT_TYPE,
            mecab_rc_path=settings.MECAB_RC_PATH,
        )
        logger.info("MeCabTokenizer 初始化成功")
    except Exception as e:
        logger.warning("MeCabTokenizer 初始化失败: %s", e)

    try:
        from app.core.grammar_engine_optimized import GrammarRuleEngine
        _grammar_engine = GrammarRuleEngine(rules_file=settings.GRAMMAR_RULES_FILE)
        logger.info("GrammarRuleEngine 初始化成功，规则文件: %s", settings.GRAMMAR_RULES_FILE)
    except Exception as e:
        logger.warning("GrammarRuleEngine 初始化失败: %s", e)

    try:
        from app.core.vocabulary import VocabularyLevelMapper
        _vocabulary_mapper = VocabularyLevelMapper(vocabulary_file=settings.VOCABULARY_LEVELS_FILE)
        logger.info("VocabularyLevelMapper 初始化成功，词汇文件: %s", settings.VOCABULARY_LEVELS_FILE)
    except Exception as e:
        logger.warning("VocabularyLevelMapper 初始化失败: %s", e)

    # LLM 客户端（可选，用于 AI 分析接口）
    _llm_client = LLMAnalysisClient(
        api_key=settings.LLM_API_KEY,
        model=settings.LLM_MODEL,
        base_url=settings.LLM_BASE_URL,
        timeout=settings.LLM_TIMEOUT,
        temperature=settings.LLM_TEMPERATURE,
    )

    if _llm_client.is_configured:
        logger.info("LLM 客户端已配置: %s", settings.LLM_MODEL)
    else:
        logger.warning("LLM_API_KEY 未配置，AI 分析接口不可用")

    # 缓存初始化
    if settings.CACHE_ENABLED:
        _cache_local = MemoryCache(
            ttl=settings.CACHE_TTL,
            max_size=settings.CACHE_MAX_SIZE,
            namespace=settings.CACHE_NAMESPACE_LOCAL,
        )
        _cache_ai = MemoryCache(
            ttl=settings.CACHE_TTL,
            max_size=settings.CACHE_MAX_SIZE,
            namespace=settings.CACHE_NAMESPACE_AI,
        )
        logger.info(
            "缓存已启用 (local TTL=%ds max=%d | ai TTL=%ds max=%d)",
            settings.CACHE_TTL, settings.CACHE_MAX_SIZE,
            settings.CACHE_TTL, settings.CACHE_MAX_SIZE,
        )
    else:
        _cache_local = _cache_ai = None
        logger.info("缓存未启用")

    # 本地分析总是可用（只要 tokenizer 初始化成功）
    _analysis_service = AnalysisService(
        llm_client=_llm_client if _llm_client.is_configured else None,
        tokenizer=_tokenizer,
        grammar_engine=_grammar_engine,
        vocabulary_mapper=_vocabulary_mapper,
        cache_local=_cache_local,
        cache_ai=_cache_ai,
    )
    logger.info("AnalysisService 初始化完成")


def get_analysis_service() -> AnalysisService:
    """获取分析服务实例（依赖注入）"""
    from fastapi import HTTPException

    if _analysis_service is None:
        raise HTTPException(
            status_code=500,
            detail="分析服务未正确初始化，请重启服务"
        )
    return _analysis_service
