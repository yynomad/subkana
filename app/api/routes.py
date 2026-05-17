"""
API 路由定义
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from app.api.models import AnalyzeRequest
from app.core.service import AnalysisService
from app.core.models import AnalyzeResponse
from app.dependencies import get_analysis_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    request: AnalyzeRequest,
    service: AnalysisService = Depends(get_analysis_service)
) -> AnalyzeResponse:
    """
    本地分析日语句子（快速，无需 API key）

    使用 MeCab 形态素分析 + 句型规则匹配 + 词汇等级映射。
    返回 tokens（带 JLPT 等级）和 grammar_patterns。
    """
    sentence = request.sentence.strip()
    if not sentence:
        raise HTTPException(status_code=400, detail="句子不能为空")

    try:
        logger.info(f"本地分析句子: {sentence}")
        return service.analyze_local(sentence, request.target_language)
    except Exception as e:
        logger.error(f"本地分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"分析过程中出现错误: {str(e)}"
        )


@router.post("/analyze/ai", response_model=AnalyzeResponse)
async def analyze_ai(
    request: AnalyzeRequest,
    service: AnalysisService = Depends(get_analysis_service)
) -> AnalyzeResponse:
    """
    AI 深度分析日语句子（需要配置 LLM_API_KEY）

    调用大模型生成翻译、句式拆分、词汇详解和学习提示。
    返回完整的 analysis 字段。
    """
    sentence = request.sentence.strip()
    if not sentence:
        raise HTTPException(status_code=400, detail="句子不能为空")

    if not service.llm_client:
        raise HTTPException(
            status_code=503,
            detail="AI 分析未启用，请配置 LLM_API_KEY 后重启服务"
        )

    try:
        logger.info(f"AI 分析句子: {sentence}")
        return service.analyze_with_ai(sentence, request.target_language)
    except Exception as e:
        logger.error(f"AI 分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"AI 分析过程中出现错误: {str(e)}"
        )


@router.get("/health")
async def health() -> Dict[str, Any]:
    """健康检查接口"""
    import app.dependencies as deps

    return {
        "status": "ok" if deps._analysis_service else "degraded",
        "components": {
            "tokenizer": deps._tokenizer is not None,
            "grammar_engine": deps._grammar_engine is not None,
            "vocabulary_mapper": deps._vocabulary_mapper is not None,
            "llm_client": deps._llm_client is not None,
            "llm_configured": bool(deps._llm_client and deps._llm_client.is_configured),
            "cache": deps._cache_local is not None and deps._cache_ai is not None,
        },
        "analysis_service": deps._analysis_service is not None,
    }


@router.get("/cache/stats")
async def cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    import app.dependencies as deps

    local = deps._cache_local
    ai = deps._cache_ai

    def _stat(cache):
        if cache is None:
            return None
        s = cache.stats()
        return {
            "size": s.size,
            "capacity": s.capacity,
            "hits": s.hits,
            "misses": s.misses,
            "evictions": s.evictions,
            "hit_rate": round(s.hit_rate, 4),
        }

    return {
        "enabled": local is not None,
        "local": _stat(local),
        "ai": _stat(ai),
    }


@router.delete("/cache")
async def clear_cache() -> Dict[str, str]:
    """清空所有缓存"""
    import app.dependencies as deps

    if deps._cache_local:
        deps._cache_local.clear()
    if deps._cache_ai:
        deps._cache_ai.clear()

    return {"status": "cache cleared"}
