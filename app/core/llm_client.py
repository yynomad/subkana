"""
LLM 客户端

通过 OpenAI 兼容的 Chat Completions 接口调用大模型，要求模型返回结构化 JSON，
让项目从本地规则库/词库驱动转为大模型驱动的日语学习分析。
"""

import json
import logging
from typing import Any, Dict, List, Optional

import requests

from app.core.models import LearningAnalysis, LearningLanguage

logger = logging.getLogger(__name__)


class LLMClientError(RuntimeError):
    """大模型调用或解析失败"""


class LLMAnalysisClient:
    """OpenAI 兼容的大模型分析客户端"""

    def __init__(
        self,
        api_key: Optional[str],
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 60,
        temperature: float = 0.2,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.temperature = temperature

    @property
    def is_configured(self) -> bool:
        """是否已配置可用的 API Key"""

        return bool(self.api_key)

    def analyze(self, sentence: str, target_language: LearningLanguage) -> LearningAnalysis:
        """调用大模型分析日语句子"""

        if not self.is_configured:
            raise LLMClientError("LLM_API_KEY 未配置，无法调用大模型分析")

        messages = self._build_messages(sentence, target_language)
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("大模型接口调用失败: %s", exc, exc_info=True)
            raise LLMClientError(f"大模型接口调用失败: {exc}") from exc

        try:
            content = response.json()["choices"][0]["message"]["content"]
            data = json.loads(content)
            return LearningAnalysis.model_validate(data)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValueError) as exc:
            logger.error("大模型返回格式无法解析: %s", exc, exc_info=True)
            raise LLMClientError(f"大模型返回格式无法解析: {exc}") from exc

    def _build_messages(self, sentence: str, target_language: LearningLanguage) -> List[Dict[str, str]]:
        language_name = "中文" if target_language == "zh" else "English"
        return [
            {
                "role": "system",
                "content": (
                    "你是一个专业的日语字幕学习助手，不是普通翻译工具。"
                    "请面向日语学习者分析句子，重点输出：1.自然翻译，2.句式/语法拆分，"
                    "3.重点单词和表达的 JLPT 等级、读音、含义与语气。"
                    "分析必须结合上下文中的真实用法，说明字面义和常见引申义。"
                    "只返回合法 JSON，不要返回 Markdown。"
                ),
            },
            {
                "role": "user",
                "content": self._build_user_prompt(sentence, target_language, language_name),
            },
        ]

    @staticmethod
    def _build_user_prompt(sentence: str, target_language: LearningLanguage, language_name: str) -> str:
        return f"""
请用{language_name}分析下面这句日语字幕：
{sentence}

输出必须是 JSON object，完全符合这个结构：
{{
  "translation": {{
    "language": "{target_language}",
    "text": "自然译文"
  }},
  "sentence_patterns": [
    {{
      "name": "句式或语法点，例如 〜てしまう",
      "jlpt_level": "N5/N4/N3/N2/N1 或 null",
      "explanation": "说明这个句式在本句中的含义，必要时包含懊悔、不小心、完成、引申义等语感",
      "components": [
        {{"text": "片段", "role": "作用", "meaning": "意思", "note": "补充或 null"}}
      ],
      "examples": ["短例句 + 翻译"]
    }}
  ],
  "vocabulary": [
    {{
      "surface": "原文形式",
      "lemma": "辞书形/原形",
      "reading": "假名读音或 null",
      "romaji": "罗马音或 null",
      "pos": "词性或 null",
      "jlpt_level": "N5/N4/N3/N2/N1 或 null",
      "meaning": "{language_name}释义，优先解释本句意思",
      "nuance": "搭配、语气、常见口语用法或 null"
    }}
  ],
  "notes": ["其他学习提示"]
}}

要求：
- 不要只翻译，要像日语学习工具一样拆分。
- 如果一个词有字面义和引申义，都要说明常用语境。
- JLPT 等级不确定时可填 null，不要编造。
""".strip()
