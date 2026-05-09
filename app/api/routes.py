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
    分析日语句子，返回面向学习者的翻译、句式拆分和重点单词

    请求体：
    {
      "sentence": "なめてしまいました",
      "target_language": "zh"
    }

    返回：
    {
      "sentence": "...",
      "target_language": "zh",
      "analysis": {
        "translation": {...},
        "sentence_patterns": [...],
        "vocabulary": [...],
        "notes": [...]
      },
      "grammar_patterns": [...],  // 旧版兼容
      "tokens": [...]             // 旧版兼容
    }
    """
    sentence = request.sentence.strip()
    if not sentence:
        raise HTTPException(status_code=400, detail="句子不能为空")

    try:
        logger.info(f"分析句子: {sentence}")
        response = service.analyze(sentence, request.target_language)
        return response
    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"分析过程中出现错误: {str(e)}"
        )

@router.get("/health")
async def health() -> Dict[str, Any]:
    """
    健康检查接口

    返回服务状态和组件初始化情况
    """
    from app.dependencies import _llm_client, _analysis_service

    return {
        "status": "ok" if _analysis_service else "degraded",
        "components": {
            "llm_client": _llm_client is not None,
            "llm_configured": bool(_llm_client and _llm_client.is_configured),
            "tokenizer": False,
            "grammar_engine": False,
            "vocabulary_mapper": False
        },
        "analysis_service": _analysis_service is not None
    }
