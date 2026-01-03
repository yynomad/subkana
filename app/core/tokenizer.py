"""
MeCabTokenizer - 封装 MeCab 形态素分析器

为什么句型识别必须基于形态素分析：
1. 日语是黏着语，语法信息（活用形、助词、助动词）都附着在词干上
2. 只有通过形态素分析才能准确提取：
   - 词干（lemma）：用于词汇等级查询
   - 活用形（conj）：用于句型匹配（如"未然形"+"なければ"）
   - 词性（pos）：区分动词、助动词、助词等
3. 单纯字符串匹配无法处理同形异义（如"行く"的未然形"行か" vs "行く"的连用形"行き"）
"""

import MeCab
from typing import List
import logging

from app.core.models import Token

logger = logging.getLogger(__name__)


class MeCabTokenizer:
    """封装 MeCab 形态素分析器"""
    
    def __init__(self, dict_type: str = "ipadic", mecab_rc_path: str = None):
        """
        初始化 MeCab Tagger
        
        Args:
            dict_type: 词典类型（ipadic, unidic 等）
            mecab_rc_path: MeCab 配置文件路径（可选）
        """
        try:
            # 设置 MECABRC 环境变量（如果提供）
            if mecab_rc_path:
                import os
                os.environ['MECABRC'] = mecab_rc_path
                logger.info(f"设置 MECABRC={mecab_rc_path}")
            
            self.tagger = MeCab.Tagger()
            logger.info(f"MeCab 初始化成功，词典类型: {dict_type}")
        except RuntimeError as e:
            logger.error(f"MeCab 初始化失败: {e}")
            raise RuntimeError(
                f"MeCab 初始化失败。请确保系统已安装 MeCab 和 IPADIC 词典。"
                f"错误信息: {e}"
            )
    
    def tokenize(self, sentence: str) -> List[Token]:
        """
        对句子进行形态素分析
        
        Args:
            sentence: 输入的日语句子
            
        Returns:
            Token 对象列表
        """
        if not sentence:
            return []
        
        try:
            # MeCab 解析
            node = self.tagger.parseToNode(sentence)
            
            tokens = []
            while node:
                # MeCab 输出格式：surface\tpos,pos1,pos2,pos3,conj,lemma,lemma_read,lemma_read2
                # 跳过 BOS/EOS 节点
                if node.surface:
                    features = node.feature.split(',')
                    
                    # 提取词性（第一个字段）
                    pos = features[0] if len(features) > 0 else ""
                    
                    # 提取活用形（第 5 个字段，索引 5）
                    conj = features[5] if len(features) > 5 else ""
                    
                    # 提取词干（第 6 个字段，索引 6）
                    # 如果词干为空或为"*"，使用 surface
                    lemma = features[6] if len(features) > 6 and features[6] != "*" else node.surface
                    
                    token = Token(
                        surface=node.surface,
                        lemma=lemma,
                        pos=pos,
                        conj=conj
                    )
                    tokens.append(token)
                
                node = node.next
            
            logger.debug(f"句子 '{sentence}' 分析出 {len(tokens)} 个 token")
            return tokens
        
        except Exception as e:
            logger.error(f"形态素分析失败: {e}")
            raise

