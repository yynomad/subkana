"""
GrammarRuleEngine - 优化版句型规则匹配引擎

优化点：
1. 支持跳过助词匹配
2. 支持活用形变体匹配
3. 支持一个条件匹配多个连续 token
4. 支持优先级和去重
"""

import json
import logging
from typing import List, Dict, Optional, Set, Tuple
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
    
    def __repr__(self):
        return f"GrammarMatch({self.rule_name}, {self.level})"


class GrammarRuleEngine:
    """优化版句型规则匹配引擎"""
    
    # 活用形变体映射
    CONJUGATION_VARIANTS = {
        # 未然形变体
        "未然形": ["未然形", "基本形"],
        # 连用形变体
        "連用形": ["連用形", "基本形", "ます形"],
        # 假定形变体
        "仮定形": ["仮定形", "基本形"],
        # 基本形
        "基本形": ["基本形"],
    }
    
    # 可以跳过的助词（不影响句型匹配）
    SKIPABLE_PARTICLES = {"は", "が", "を", "に", "で", "と", "も", "から", "まで", "の"}
    
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
        rules_path = Path(__file__).parent.parent.parent / rules_file
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            return rules
        except FileNotFoundError:
            logger.error(f"规则文件未找到：{rules_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"规则文件格式错误：{e}")
            return []
    
    def match(self, tokens: List[Token]) -> List[GrammarMatch]:
        """
        在 token 序列中匹配所有句型规则（优化版）
        
        优化：
        1. 支持跳过助词
        2. 支持活用形变体
        3. 去重（相同位置只保留最匹配的规则）
        4. 优先级排序（N5 > N4 > N3 > N2 > N1）
        
        Args:
            tokens: Token 对象列表
            
        Returns:
            匹配到的句型列表
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
                matched_indices = self._try_match_pattern_optimized(
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
        
        # 去重和排序
        matches = self._deduplicate_and_sort(matches)
        
        if matches:
            logger.info(f"匹配到 {len(matches)} 个句型")
        return matches
    
    def _try_match_pattern_optimized(
        self,
        tokens: List[Token],
        start_idx: int,
        pattern: List[Dict]
    ) -> Optional[List[int]]:
        """
        优化版：尝试从指定位置匹配规则 pattern
        
        优化：
        1. 支持跳过助词
        2. 支持活用形变体
        3. 支持模糊匹配
        
        Args:
            tokens: Token 列表
            start_idx: 起始位置
            pattern: 规则 pattern（条件列表）
            
        Returns:
            如果匹配成功，返回匹配的 token 索引列表；否则返回 None
        """
        matched_indices = []
        current_idx = start_idx
        pattern_idx = 0
        
        while pattern_idx < len(pattern) and current_idx < len(tokens):
            condition = pattern[pattern_idx]
            token = tokens[current_idx]
            
            # 检查是否应该跳过这个 token（助词）
            if self._should_skip_token(token) and not self._is_condition_for_particle(condition):
                current_idx += 1
                continue
            
            # 检查条件是否匹配
            if self._match_condition_optimized(token, condition):
                matched_indices.append(current_idx)
                pattern_idx += 1
            
            current_idx += 1
        
        # 所有条件都匹配成功
        if pattern_idx == len(pattern):
            return matched_indices
        
        return None
    
    def _should_skip_token(self, token: Token) -> bool:
        """判断是否应该跳过这个 token（助词）"""
        return token.pos == "助詞" and token.surface in self.SKIPABLE_PARTICLES
    
    def _is_condition_for_particle(self, condition: Dict) -> bool:
        """判断条件是否专门匹配助词"""
        return condition.get("pos") == "助詞" or "surface" in condition
    
    def _match_condition_optimized(self, token: Token, condition: Dict) -> bool:
        """
        优化版：检查单个 token 是否匹配条件
        
        优化：
        1. 支持活用形变体
        2. 支持部分匹配
        
        Args:
            token: Token 对象
            condition: 匹配条件
            
        Returns:
            是否匹配
        """
        # 如果条件中指定了 pos，必须匹配
        if "pos" in condition:
            if token.pos != condition["pos"]:
                return False
        
        # 如果条件中指定了 conj，支持变体匹配
        if "conj" in condition:
            target_conj = condition["conj"]
            # 获取所有可接受的变体
            acceptable_conjs = self.CONJUGATION_VARIANTS.get(target_conj, [target_conj])
            if token.conj not in acceptable_conjs:
                # 如果是基本形或未指定，也接受
                if token.conj != "*" and token.conj != "基本形":
                    return False
        
        # 如果条件中指定了 lemma，必须匹配
        if "lemma" in condition:
            if token.lemma != condition["lemma"]:
                return False
        
        # 如果条件中指定了 surface，必须匹配（或部分匹配）
        if "surface" in condition:
            target_surface = condition["surface"]
            # 支持部分匹配（如"～ので"匹配"ので"）
            if target_surface.startswith("～"):
                if not token.surface.endswith(target_surface[1:]):
                    return False
            elif token.surface != target_surface:
                return False
        
        return True
    
    def _extract_structure(self, tokens: List[Token], indices: List[int]) -> List[str]:
        """提取匹配部分的表面形式"""
        return [tokens[i].surface for i in indices]
    
    def _deduplicate_and_sort(self, matches: List[GrammarMatch]) -> List[GrammarMatch]:
        """
        去重和排序
        
        规则：
        1. 相同位置的匹配只保留一个
        2. 优先级：N5 > N4 > N3 > N2 > N1
        3. 更长的匹配优先
        """
        if not matches:
            return matches
        
        # 按位置分组
        position_matches = {}
        for match in matches:
            key = tuple(match.matched_token_indices)
            if key not in position_matches:
                position_matches[key] = []
            position_matches[key].append(match)
        
        # 每组选择最佳匹配
        level_priority = {"N5": 5, "N4": 4, "N3": 3, "N2": 2, "N1": 1}
        result = []
        
        for key, group in position_matches.items():
            # 排序：优先级高的在前，匹配长度长的在前
            group.sort(
                key=lambda m: (
                    level_priority.get(m.level, 0),
                    len(m.matched_token_indices)
                ),
                reverse=True
            )
            result.append(group[0])  # 选择最佳匹配
        
        return result
