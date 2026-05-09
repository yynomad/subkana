"""
API 请求/响应模型
"""

from pydantic import BaseModel, Field

from app.core.models import LearningLanguage


class AnalyzeRequest(BaseModel):
    """分析请求模型"""

    sentence: str = Field(..., min_length=1, description="要分析的日语句子")
    target_language: LearningLanguage = Field(
        default="zh",
        description="学习者使用的解释语言：zh（中文）或 en（English）",
    )


class HealthResponse(BaseModel):
    """健康检查响应模型"""

    status: str
    components: dict
