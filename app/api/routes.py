"""
API 路由定义
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Response
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
    分析日语句子，返回句型结构和单词等级

    请求体：
    {
      "sentence": "行かなければなりません"
    }

    返回：
    {
      "sentence": "...",
      "grammar_patterns": [...],
      "tokens": [...]
    }
    """
    sentence = request.sentence.strip()
    if not sentence:
        raise HTTPException(status_code=400, detail="句子不能为空")

    try:
        logger.info(f"分析句子: {sentence}")
        response = service.analyze(sentence)
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
    from app.dependencies import _tokenizer, _grammar_engine, _vocabulary_mapper, _analysis_service

    return {
        "status": "ok" if _analysis_service else "degraded",
        "components": {
            "tokenizer": _tokenizer is not None,
            "grammar_engine": _grammar_engine is not None,
            "vocabulary_mapper": _vocabulary_mapper is not None
        },
        "analysis_service": _analysis_service is not None
    }
    

