"""
VocabularyLevelMapper - 词汇等级映射器

将词干（lemma）映射到 JLPT 等级（N1-N5）
当前使用简化的 mock 数据，后续可扩展为完整词表
"""

import json
import logging
from typing import Optional
from pathlib import Path

from app.core.models import Token

logger = logging.getLogger(__name__)


class VocabularyLevelMapper:
    """词汇等级映射器"""
    
    def __init__(self, vocabulary_file: str = "data/vocabulary_levels.json"):
        """
        初始化词汇映射器
        
        Args:
            vocabulary_file: 词汇等级 JSON 文件路径
        """
        self.vocab_map = self._load_vocabulary(vocabulary_file)
        logger.info(f"加载了 {len(self.vocab_map)} 个词汇等级映射")
    
    def _load_vocabulary(self, vocabulary_file: str) -> dict:
        """加载词汇等级映射"""
        vocab_path = Path(__file__).parent.parent.parent / vocabulary_file
        try:
            with open(vocab_path, 'r', encoding='utf-8') as f:
                vocab_map = json.load(f)
            return vocab_map
        except FileNotFoundError:
            logger.warning(f"词汇文件未找到: {vocab_path}，使用空映射")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"词汇文件格式错误: {e}")
            raise ValueError(f"词汇文件格式错误: {e}")
    
    def get_level(self, token: Token) -> Optional[str]:
        """
        获取 token 的 JLPT 等级
        
        Args:
            token: Token 对象
            
        Returns:
            JLPT 等级（N1-N5），如果未找到则返回 None
        """
        # 优先使用 lemma 查找
        level = self.vocab_map.get(token.lemma)
        
        # 如果 lemma 未找到，尝试使用 surface
        if level is None:
            level = self.vocab_map.get(token.surface)
        
        return level

