"""
GrammarRuleEngine - 句型规则匹配引擎

核心设计：
1. 基于形态素分析结果进行匹配，而非字符串匹配
2. 使用滑动窗口算法，支持一句中匹配多个句型
3. 规则定义与匹配逻辑分离，便于扩展新句型
"""

import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

from app.core.models import Token

logger = logging.getLogger(__name__)


class GrammarMatch:
    """句型匹配结果"""
    def __init__(
        self,
        rule_id: str,
        rule_name: str,
        level: str,
        meaning: str,
        matched_token_indices: List[int],
        structure: List[str]
    ):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.level = level
        self.meaning = meaning
        self.matched_token_indices = matched_token_indices
        self.structure = structure


class GrammarRuleEngine:
    """句型规则匹配引擎"""
    
    def __init__(self, rules_file: str = "data/grammar_rules.json"):
        """
        初始化规则引擎
        
        Args:
            rules_file: 句型规则 JSON 文件路径
        """
        self.rules = self._load_rules(rules_file)
        logger.info(f"加载了 {len(self.rules)} 条句型规则")
    
    def _load_rules(self, rules_file: str) -> List[Dict]:
        """加载句型规则"""
        # 从项目根目录查找文件
        rules_path = Path(__file__).parent.parent.parent / rules_file
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            return rules
        except FileNotFoundError:
            logger.error(f"规则文件未找到: {rules_path}")
            raise FileNotFoundError(f"规则文件未找到: {rules_path}")
        except json.JSONDecodeError as e:
            logger.error(f"规则文件格式错误: {e}")
            raise ValueError(f"规则文件格式错误: {e}")
    
    def match(self, tokens: List[Token]) -> List[GrammarMatch]:
        """
        在 token 序列中匹配所有句型规则
        
        算法：滑动窗口匹配
        1. 遍历每个可能的起始位置
        2. 对每个起始位置，尝试匹配所有规则
        3. 规则 pattern 中的每个条件必须按序匹配
        
        Args:
            tokens: Token 对象列表
            
        Returns:
            匹配到的句型列表（可能有多个）
        """
        matches = []
        
        if not tokens:
            return matches
        
        # 对每个可能的起始位置
        for start_idx in range(len(tokens)):
            # 尝试匹配每个规则
            for rule in self.rules:
                pattern = rule.get("pattern", [])
                if not pattern:
                    continue
                
                # 尝试从当前起始位置匹配这个规则
                matched_indices = self._try_match_pattern(
                    tokens, start_idx, pattern
                )
                
                if matched_indices:
                    # 匹配成功，创建 GrammarMatch 对象
                    match = GrammarMatch(
                        rule_id=rule["id"],
                        rule_name=rule["name"],
                        level=rule["level"],
                        meaning=rule.get("meaning", ""),
                        matched_token_indices=matched_indices,
                        structure=self._extract_structure(tokens, matched_indices)
                    )
                    matches.append(match)
        
        if matches:
            logger.debug(f"匹配到 {len(matches)} 个句型")
        return matches
    
    def _try_match_pattern(
        self,
        tokens: List[Token],
        start_idx: int,
        pattern: List[Dict]
    ) -> Optional[List[int]]:
        """
        尝试从指定位置匹配规则 pattern
        
        Args:
            tokens: Token 列表
            start_idx: 起始位置
            pattern: 规则 pattern（条件列表）
            
        Returns:
            如果匹配成功，返回匹配的 token 索引列表；否则返回 None
        """
        matched_indices = []
        current_idx = start_idx
        
        for condition_idx, condition in enumerate(pattern):
            # 如果已经超出 token 范围，匹配失败
            if current_idx >= len(tokens):
                return None
            
            token = tokens[current_idx]
            
            # 检查条件是否匹配
            # 条件中的字段（pos/conj/lemma/surface）如果存在，必须全部匹配
            if not self._match_condition(token, condition):
                return None
            
            matched_indices.append(current_idx)
            current_idx += 1
        
        # 所有条件都匹配成功
        return matched_indices
    
    def _match_condition(self, token: Token, condition: Dict) -> bool:
        """
        检查单个 token 是否匹配条件
        
        Args:
            token: Token 对象
            condition: 匹配条件（可能包含 pos, conj, lemma, surface）
            
        Returns:
            是否匹配
        """
        # 如果条件中指定了 pos，必须匹配
        if "pos" in condition:
            if token.pos != condition["pos"]:
                return False
        
        # 如果条件中指定了 conj，必须匹配
        if "conj" in condition:
            if token.conj != condition["conj"]:
                return False
        
        # 如果条件中指定了 lemma，必须匹配
        if "lemma" in condition:
            if token.lemma != condition["lemma"]:
                return False
        
        # 如果条件中指定了 surface，必须匹配
        if "surface" in condition:
            if token.surface != condition["surface"]:
                return False
        
        return True
    
    def _extract_structure(self, tokens: List[Token], indices: List[int]) -> List[str]:
        """
        提取匹配部分的表面形式，用于显示结构
        
        Args:
            tokens: Token 列表
            indices: 匹配的 token 索引
            
        Returns:
            表面形式列表
        """
        return [tokens[i].surface for i in indices]

