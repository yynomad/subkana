"""
分析服务 - 使用大模型生成日语学习分析
"""

import logging
from typing import List

from app.core.llm_client import LLMAnalysisClient
from app.core.models import (
    AnalyzeResponse,
    GrammarPattern,
    LearningAnalysis,
    LearningLanguage,
    Token,
)

logger = logging.getLogger(__name__)


class AnalysisService:
    """句子分析服务"""

    def __init__(self, llm_client: LLMAnalysisClient):
        """
        初始化分析服务

        Args:
            llm_client: 大模型分析客户端
        """
        self.llm_client = llm_client

    def analyze(self, sentence: str, target_language: LearningLanguage = "zh") -> AnalyzeResponse:
        """
        分析日语句子，返回面向学习者的翻译、句式拆分和重点单词

        Args:
            sentence: 输入的日语句子
            target_language: 学习者使用的解释语言，zh 或 en

        Returns:
            AnalyzeResponse 对象
        """
        analysis = self.llm_client.analyze(sentence, target_language)

        return AnalyzeResponse(
            sentence=sentence,
            target_language=target_language,
            analysis=analysis,
            grammar_patterns=self._to_legacy_grammar_patterns(sentence, analysis),
            tokens=self._to_legacy_tokens(analysis),
        )

    @staticmethod
    def _to_legacy_grammar_patterns(sentence: str, analysis: LearningAnalysis) -> List[GrammarPattern]:
        """
        将大模型句式结果映射为旧版 grammar_patterns，兼容已有前端。
        新前端应优先使用 analysis.sentence_patterns。
        """

        grammar_patterns: List[GrammarPattern] = []
        for index, pattern in enumerate(analysis.sentence_patterns):
            structure = [component.text for component in pattern.components]
            grammar_patterns.append(
                GrammarPattern(
                    id=f"llm_pattern_{index + 1}",
                    name=pattern.name,
                    level=pattern.jlpt_level or "",
                    meaning=pattern.explanation,
                    structure=structure,
                    span={"start": 0, "end": len(sentence)},
                    matched_tokens=list(range(len(structure))),
                )
            )
        return grammar_patterns

    @staticmethod
    def _to_legacy_tokens(analysis: LearningAnalysis) -> List[Token]:
        """
        将大模型重点词结果映射为旧版 tokens，兼容已有前端。
        新前端应优先使用 analysis.vocabulary。
        """

        return [
            Token(
                surface=item.surface,
                lemma=item.lemma,
                pos=item.pos or "",
                jlpt_level=item.jlpt_level,
                reading=item.reading,
                meaning=item.meaning,
                romaji=item.romaji,
            )
            for item in analysis.vocabulary
        ]
