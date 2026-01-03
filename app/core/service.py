"""
分析服务 - 整合所有核心功能
"""

import logging
from typing import List

from app.core.models import Token, GrammarPattern, AnalyzeResponse
from app.core.tokenizer import MeCabTokenizer
from app.core.grammar_engine import GrammarRuleEngine, GrammarMatch
from app.core.vocabulary import VocabularyLevelMapper

logger = logging.getLogger(__name__)


class AnalysisService:
    """句子分析服务"""
    
    def __init__(
        self,
        tokenizer: MeCabTokenizer,
        grammar_engine: GrammarRuleEngine,
        vocabulary_mapper: VocabularyLevelMapper
    ):
        """
        初始化分析服务
        
        Args:
            tokenizer: MeCab 分词器
            grammar_engine: 句型规则引擎
            vocabulary_mapper: 词汇等级映射器
        """
        self.tokenizer = tokenizer
        self.grammar_engine = grammar_engine
        self.vocabulary_mapper = vocabulary_mapper
    
    def analyze(self, sentence: str) -> AnalyzeResponse:
        """
        分析日语句子
        
        Args:
            sentence: 输入的日语句子
            
        Returns:
            AnalyzeResponse 对象
        """
        # 1. 形态素分析
        tokens = self.tokenizer.tokenize(sentence)
        
        if not tokens:
            return AnalyzeResponse(
                sentence=sentence,
                grammar_patterns=[],
                tokens=[]
            )
        
        # 2. 句型匹配
        grammar_matches = self.grammar_engine.match(tokens)
        
        # 3. 添加词汇信息到 tokens（等级、读音、意思、罗马音）
        tokens_with_info = []
        for token in tokens:
            enriched_token = self.vocabulary_mapper.enrich_token(token)
            tokens_with_info.append(enriched_token)
        
        # 4. 转换 grammar_matches 为 GrammarPattern
        grammar_patterns = []
        for match in grammar_matches:
            span = self._calculate_span(sentence, tokens, match.matched_token_indices)
            pattern = GrammarPattern(
                id=match.rule_id,
                name=match.rule_name,
                level=match.level,
                meaning=match.meaning,
                structure=match.structure,
                span=span,
                matched_tokens=match.matched_token_indices
            )
            grammar_patterns.append(pattern)
        
        return AnalyzeResponse(
            sentence=sentence,
            grammar_patterns=grammar_patterns,
            tokens=tokens_with_info
        )
    
    @staticmethod
    def _calculate_span(
        sentence: str,
        tokens: List[Token],
        matched_indices: List[int]
    ) -> dict:
        """
        计算匹配的 token 在原始句子中的字符位置范围（span）
        
        Args:
            sentence: 原始句子
            tokens: Token 列表
            matched_indices: 匹配的 token 索引列表
            
        Returns:
            包含 start 和 end 的字典
        """
        if not matched_indices:
            return {"start": 0, "end": 0}
        
        # 找到第一个和最后一个匹配 token 的 surface
        first_token = tokens[matched_indices[0]]
        last_token = tokens[matched_indices[-1]]
        
        # 在原始句子中查找第一个 token 的起始位置
        start = sentence.find(first_token.surface)
        if start == -1:
            # 如果找不到，使用累加方式估算
            start = sum(len(tokens[i].surface) for i in range(matched_indices[0]))
        
        # 计算最后一个 token 的结束位置
        end = start
        for idx in matched_indices:
            token = tokens[idx]
            # 在句子中查找当前 token 的位置
            token_pos = sentence.find(token.surface, end)
            if token_pos != -1:
                end = token_pos + len(token.surface)
            else:
                # 如果找不到，累加长度
                end += len(token.surface)
        
        return {"start": start, "end": end}

