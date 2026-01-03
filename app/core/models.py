"""
数据模型定义
"""

from typing import List, Optional
from pydantic import BaseModel


class VocabularyInfo(BaseModel):
    """词汇详细信息"""
    level: Optional[str] = None      # JLPT 等级 (N1-N5)
    reading: Optional[str] = None    # 读音（假名）
    meaning: Optional[str] = None    # 意思（英文/中文）
    romaji: Optional[str] = None     # 罗马音


class Token(BaseModel):
    """标准化的 token 数据结构"""
    surface: str  # 表面形式（原文中的实际字符）
    lemma: str    # 词干/原形
    pos: str       # 词性（如：動詞、助動詞、助詞）
    conj: str = "" # 活用形（如：未然形、連用形、終止形）
    jlpt_level: Optional[str] = None  # JLPT 等级
    reading: Optional[str] = None     # 读音（假名）
    meaning: Optional[str] = None     # 意思
    romaji: Optional[str] = None      # 罗马音


class GrammarPattern(BaseModel):
    """句型匹配结果"""
    id: str
    name: str
    level: str
    meaning: str
    structure: List[str]
    span: dict  # {"start": int, "end": int}
    matched_tokens: List[int]


class AnalyzeResponse(BaseModel):
    """分析响应模型"""
    sentence: str
    grammar_patterns: List[GrammarPattern]
    tokens: List[Token]

