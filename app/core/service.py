"""
分析服务 - 支持本地分析和 AI 分析两种模式
"""

import hashlib
import logging
from typing import List, Optional

from app.core.cache import MemoryCache
from app.core.llm_client import LLMAnalysisClient
from app.core.models import (
    AnalyzeResponse,
    GrammarPattern,
    LearningAnalysis,
    LearningLanguage,
    Token,
)

logger = logging.getLogger(__name__)


def _make_cache_key(sentence: str, target_language: str) -> str:
    """生成缓存键：对句子和语言取 SHA-256 摘要"""
    raw = f"{sentence}||{target_language}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class AnalysisService:
    """句子分析服务"""

    def __init__(
        self,
        llm_client: Optional[LLMAnalysisClient] = None,
        tokenizer=None,
        grammar_engine=None,
        vocabulary_mapper=None,
        cache_local: Optional[MemoryCache] = None,
        cache_ai: Optional[MemoryCache] = None,
    ):
        self.llm_client = llm_client
        self.tokenizer = tokenizer
        self.grammar_engine = grammar_engine
        self.vocabulary_mapper = vocabulary_mapper
        self.cache_local = cache_local
        self.cache_ai = cache_ai

    # ── AI 分析 ──────────────────────────────────────────────

    def analyze_with_ai(self, sentence: str, target_language: LearningLanguage = "zh") -> AnalyzeResponse:
        """调用大模型分析日语句子（带缓存）"""
        if not self.llm_client:
            raise RuntimeError("LLM client 未配置")

        # 查缓存
        cached = self._get_from_cache(self.cache_ai, sentence, target_language)
        if cached is not None:
            logger.info("AI 分析缓存命中: %s", sentence)
            return cached

        analysis = self.llm_client.analyze(sentence, target_language)
        result = AnalyzeResponse(
            sentence=sentence,
            target_language=target_language,
            analysis=analysis,
            grammar_patterns=self._ai_to_grammar_patterns(sentence, analysis),
            tokens=self._ai_to_tokens(analysis),
        )

        # 写入缓存
        self._set_to_cache(self.cache_ai, sentence, target_language, result)
        return result

    # ── 本地分析 ─────────────────────────────────────────────

    def analyze_local(self, sentence: str, target_language: LearningLanguage = "zh") -> AnalyzeResponse:
        """使用本地 MeCab + 规则引擎 + 词库进行分析（带缓存）"""
        if not self.tokenizer:
            raise RuntimeError("本地分析组件未初始化")

        # 查缓存
        cached = self._get_from_cache(self.cache_local, sentence, target_language)
        if cached is not None:
            logger.info("本地分析缓存命中: %s", sentence)
            return cached

        tokens = self.tokenizer.tokenize(sentence)
        if self.vocabulary_mapper:
            tokens = [self.vocabulary_mapper.enrich_token(t) for t in tokens]

        grammar_patterns: List[GrammarPattern] = []
        if self.grammar_engine:
            matches = self.grammar_engine.match(tokens)
            grammar_patterns = self._matches_to_grammar_patterns(tokens, matches)

        result = AnalyzeResponse(
            sentence=sentence,
            target_language=target_language,
            analysis=None,
            tokens=tokens,
            grammar_patterns=grammar_patterns,
        )

        # 写入缓存
        self._set_to_cache(self.cache_local, sentence, target_language, result)
        return result

    # ── 转换工具 ─────────────────────────────────────────────

    @staticmethod
    def _matches_to_grammar_patterns(tokens: List[Token], matches) -> List[GrammarPattern]:
        """将 GrammarMatch 列表转为 GrammarPattern 列表，计算 token span"""
        results: List[GrammarPattern] = []
        # 预计算每个 token 在句子中的字符位置
        token_spans: List[tuple[int, int]] = []
        pos = 0
        for t in tokens:
            start = pos
            end = pos + len(t.surface)
            token_spans.append((start, end))
            pos = end

        for m in matches:
            indices = m.matched_token_indices
            if indices:
                span_start = token_spans[indices[0]][0]
                span_end = token_spans[indices[-1]][1]
            else:
                span_start = span_end = 0
            results.append(GrammarPattern(
                id=m.rule_id,
                name=m.rule_name,
                level=m.level,
                meaning=m.meaning,
                structure=m.structure,
                span={"start": span_start, "end": span_end},
                matched_tokens=indices,
            ))
        return results

    @staticmethod
    def _ai_to_grammar_patterns(sentence: str, analysis: LearningAnalysis) -> List[GrammarPattern]:
        """将大模型句式结果映射为旧版 grammar_patterns"""
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
    def _ai_to_tokens(analysis: LearningAnalysis) -> List[Token]:
        """将大模型重点词结果映射为旧版 tokens"""
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

    # ── 缓存辅助 ─────────────────────────────────────────────

    @staticmethod
    def _get_from_cache(
        cache: Optional[MemoryCache],
        sentence: str,
        target_language: str,
    ) -> Optional[AnalyzeResponse]:
        """从缓存中获取分析结果"""
        if cache is None:
            return None
        key = _make_cache_key(sentence, target_language)
        return cache.get(key)

    @staticmethod
    def _set_to_cache(
        cache: Optional[MemoryCache],
        sentence: str,
        target_language: str,
        result: AnalyzeResponse,
    ) -> None:
        """将分析结果写入缓存"""
        if cache is None:
            return
        key = _make_cache_key(sentence, target_language)
        cache.set(key, result)
