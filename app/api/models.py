"""
API 请求/响应模型
"""

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """分析请求模型"""
    sentence: str = Field(..., min_length=1, description="要分析的日语句子")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    components: dict

