"""
自定义异常类
"""


class AnalysisError(Exception):
    """分析相关异常基类"""
    pass


class TokenizerError(AnalysisError):
    """分词器异常"""
    pass


class GrammarEngineError(AnalysisError):
    """句型引擎异常"""
    pass


class VocabularyError(AnalysisError):
    """词汇映射异常"""
    pass

