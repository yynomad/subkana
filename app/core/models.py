"""
数据模型定义
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


LearningLanguage = Literal["zh", "en"]


class Translation(BaseModel):
    """整句翻译"""

    language: LearningLanguage = Field(..., description="解释和翻译使用的语言：zh 或 en")
    text: str = Field(..., description="面向学习者的自然译文")


class BreakdownComponent(BaseModel):
    """句式拆分中的一个组成部分"""

    text: str = Field(..., description="原句中的片段，例如 なめる 或 てしまう")
    role: str = Field(..., description="该片段在句式中的作用")
    meaning: str = Field(..., description="该片段在当前上下文中的意思")
    note: Optional[str] = Field(default=None, description="补充说明")


class SentencePattern(BaseModel):
    """句式/语法分析"""

    name: str = Field(..., description="句式名称或语法点")
    jlpt_level: Optional[str] = Field(default=None, description="大致 JLPT 等级，例如 N4")
    explanation: str = Field(..., description="面向学习者的句式解释")
    components: List[BreakdownComponent] = Field(default_factory=list, description="句式拆分")
    examples: List[str] = Field(default_factory=list, description="辅助学习例句")


class VocabularyPoint(BaseModel):
    """重点单词/表达"""

    surface: str = Field(..., description="原文中的形式")
    lemma: str = Field(..., description="辞书形/原形")
    reading: Optional[str] = Field(default=None, description="假名读音")
    romaji: Optional[str] = Field(default=None, description="罗马音")
    pos: Optional[str] = Field(default=None, description="词性")
    jlpt_level: Optional[str] = Field(default=None, description="JLPT 等级，例如 N5/N4/N3/N2/N1")
    meaning: str = Field(..., description="当前学习语言下的意思")
    nuance: Optional[str] = Field(default=None, description="语气、搭配或易错点")


class LearningAnalysis(BaseModel):
    """大模型生成的日语学习分析"""

    translation: Translation
    sentence_patterns: List[SentencePattern] = Field(default_factory=list)
    vocabulary: List[VocabularyPoint] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list, description="其他学习提示")


class VocabularyInfo(BaseModel):
    """词汇详细信息（旧版兼容）"""

    level: Optional[str] = None      # JLPT 等级 (N1-N5)
    reading: Optional[str] = None    # 读音（假名）
    meaning: Optional[str] = None    # 意思（英文/中文）
    romaji: Optional[str] = None     # 罗马音


class Token(BaseModel):
    """标准化的 token 数据结构（旧版兼容）"""

    surface: str  # 表面形式（原文中的实际字符）
    lemma: str    # 词干/原形
    pos: str       # 词性（如：動詞、助動詞、助詞）
    conj: str = "" # 活用形（如：未然形、連用形、終止形）
    jlpt_level: Optional[str] = None  # JLPT 等级
    reading: Optional[str] = None     # 读音（假名）
    meaning: Optional[str] = None     # 意思
    romaji: Optional[str] = None      # 罗马音


class GrammarPattern(BaseModel):
    """句型匹配结果（旧版兼容）"""

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
    target_language: LearningLanguage = "zh"
    analysis: LearningAnalysis
    grammar_patterns: List[GrammarPattern] = Field(default_factory=list)
    tokens: List[Token] = Field(default_factory=list)
