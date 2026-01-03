"""
VocabularyLevelMapper - 词汇等级映射器

将词干（lemma）映射到 JLPT 等级（N1-N5）
支持返回完整的词汇信息：等级、读音、意思、罗马音
"""

import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass

from app.core.models import Token

logger = logging.getLogger(__name__)


@dataclass
class VocabInfo:
    """词汇信息"""
    level: Optional[str] = None
    reading: Optional[str] = None
    meaning: Optional[str] = None
    romaji: Optional[str] = None


class VocabularyLevelMapper:
    """词汇等级映射器"""
    
    def __init__(self, vocabulary_file: str = "data/vocabulary_levels.json"):
        """
        初始化词汇映射器
        
        Args:
            vocabulary_file: 词汇等级 JSON 文件路径
        """
        self.vocab_map = self._load_vocabulary(vocabulary_file)
        logger.info(f"加载了 {len(self.vocab_map)} 个词汇映射")
    
    def _load_vocabulary(self, vocabulary_file: str) -> Dict[str, Dict[str, Any]]:
        """加载词汇数据"""
        vocab_path = Path(__file__).parent.parent.parent / vocabulary_file
        try:
            with open(vocab_path, 'r', encoding='utf-8') as f:
                raw_vocab = json.load(f)
            
            # 标准化词汇数据
            return self._normalize_vocabulary(raw_vocab)
            
        except FileNotFoundError:
            logger.warning(f"词汇文件未找到: {vocab_path}，使用空映射")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"词汇文件格式错误: {e}")
            raise ValueError(f"词汇文件格式错误: {e}")
    
    def _normalize_vocabulary(self, raw_vocab: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        标准化词汇数据格式
        
        支持两种输入格式：
        1. 简单格式: {"word": "N5"} -> {"word": {"level": "N5"}}
        2. 完整格式: {"word": {"level": "N5", "reading": "...", ...}} -> 保持不变
        """
        normalized = {}
        
        for word, value in raw_vocab.items():
            if isinstance(value, str):
                # 简单格式：只有等级
                normalized[word] = {"level": value}
            elif isinstance(value, dict):
                # 完整格式：保持原样
                normalized[word] = value
            else:
                logger.warning(f"未知词汇格式: {word} -> {value}")
        
        return normalized
    
    def get_vocab_info(self, word: str) -> Optional[VocabInfo]:
        """
        获取词汇的完整信息
        
        Args:
            word: 词汇（lemma 或 surface）
            
        Returns:
            VocabInfo 对象，如果未找到则返回 None
        """
        vocab_data = self.vocab_map.get(word)
        if vocab_data:
            return VocabInfo(
                level=vocab_data.get('level'),
                reading=vocab_data.get('reading'),
                meaning=vocab_data.get('meaning'),
                romaji=vocab_data.get('romaji')
            )
        return None
    
    def get_level(self, token: Token) -> Optional[str]:
        """
        获取 token 的 JLPT 等级（向后兼容）
        
        Args:
            token: Token 对象
            
        Returns:
            JLPT 等级（N1-N5），如果未找到则返回 None
        """
        info = self.get_token_vocab_info(token)
        return info.level if info else None
    
    def get_token_vocab_info(self, token: Token) -> Optional[VocabInfo]:
        """
        获取 token 的完整词汇信息
        
        Args:
            token: Token 对象
            
        Returns:
            VocabInfo 对象，如果未找到则返回 None
        """
        # 优先使用 lemma 查找
        info = self.get_vocab_info(token.lemma)
        
        # 如果 lemma 未找到，尝试使用 surface
        if info is None:
            info = self.get_vocab_info(token.surface)
        
        return info
    
    def enrich_token(self, token: Token) -> Token:
        """
        为 token 添加词汇信息
        
        Args:
            token: Token 对象
            
        Returns:
            添加了词汇信息的 Token 对象
        """
        info = self.get_token_vocab_info(token)
        
        if info:
            token.jlpt_level = info.level
            token.reading = info.reading
            token.meaning = info.meaning
            token.romaji = info.romaji
        
        return token
