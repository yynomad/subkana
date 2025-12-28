"""
依赖注入

管理全局服务实例
"""

import logging
from functools import lru_cache

from app.config import get_settings
from app.core.tokenizer import MeCabTokenizer
from app.core.grammar_engine import GrammarRuleEngine
from app.core.vocabulary import VocabularyLevelMapper
from app.core.service import AnalysisService

logger = logging.getLogger(__name__)

# 全局服务实例
_tokenizer: MeCabTokenizer | None = None
_grammar_engine: GrammarRuleEngine | None = None
_vocabulary_mapper: VocabularyLevelMapper | None = None
_analysis_service: AnalysisService | None = None


def init_services():
    """初始化所有服务（在应用启动时调用）"""
    global _tokenizer, _grammar_engine, _vocabulary_mapper, _analysis_service
    
    settings = get_settings()
    
    try:
        _tokenizer = MeCabTokenizer(dict_type=settings.MECAB_DICT_TYPE)
        logger.info("MeCabTokenizer 初始化成功")
    except Exception as e:
        logger.error(f"MeCabTokenizer 初始化失败: {e}")
        _tokenizer = None
    
    try:
        _grammar_engine = GrammarRuleEngine(
            rules_file=settings.GRAMMAR_RULES_FILE
        )
        logger.info("GrammarRuleEngine 初始化成功")
    except Exception as e:
        logger.error(f"GrammarRuleEngine 初始化失败: {e}")
        _grammar_engine = None
    
    try:
        _vocabulary_mapper = VocabularyLevelMapper(
            vocabulary_file=settings.VOCABULARY_LEVELS_FILE
        )
        logger.info("VocabularyLevelMapper 初始化成功")
    except Exception as e:
        logger.error(f"VocabularyLevelMapper 初始化失败: {e}")
        _vocabulary_mapper = None
    
    if _tokenizer and _grammar_engine and _vocabulary_mapper:
        _analysis_service = AnalysisService(
            tokenizer=_tokenizer,
            grammar_engine=_grammar_engine,
            vocabulary_mapper=_vocabulary_mapper
        )
        logger.info("AnalysisService 初始化成功")
    else:
        logger.warning("部分组件初始化失败，AnalysisService 未创建")


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
            detail="分析服务未正确初始化，请检查 MeCab 是否已安装"
        )
    return _analysis_service

