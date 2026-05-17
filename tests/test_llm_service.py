import unittest

from app.core.models import LearningAnalysis
from app.core.service import AnalysisService


class FakeLLMClient:
    def analyze(self, sentence, target_language):
        return LearningAnalysis.model_validate(
            {
                "translation": {"language": target_language, "text": "低估了对手。"},
                "sentence_patterns": [
                    {
                        "name": "〜てしまう",
                        "jlpt_level": "N4",
                        "explanation": "表示遗憾或不小心完成某动作。",
                        "components": [
                            {"text": "なめる", "role": "动词", "meaning": "小看/轻视"},
                            {"text": "てしまう", "role": "补助动词", "meaning": "不小心/遗憾"},
                            {"text": "ました", "role": "礼貌过去", "meaning": "过去发生"},
                        ],
                        "examples": ["相手をなめてしまいました。= 低估了对手。"],
                    }
                ],
                "vocabulary": [
                    {
                        "surface": "なめて",
                        "lemma": "なめる",
                        "reading": "なめる",
                        "romaji": "nameru",
                        "pos": "動詞",
                        "jlpt_level": "N2",
                        "meaning": "舔；小看、轻视",
                        "nuance": "口语里常用作“小看”。",
                    }
                ],
                "notes": ["没有宾语时要根据字幕上下文判断是字面义还是引申义。"],
            }
        )


class AnalysisServiceTest(unittest.TestCase):
    def test_ai_analysis_returns_full_response(self):
        """AI 分析返回完整的 analysis + legacy 字段"""
        service = AnalysisService(llm_client=FakeLLMClient())

        response = service.analyze_with_ai("なめてしまいました", "zh")

        self.assertEqual(response.target_language, "zh")
        self.assertEqual(response.analysis.translation.text, "低估了对手。")
        self.assertEqual(response.analysis.sentence_patterns[0].name, "〜てしまう")
        self.assertEqual(response.analysis.vocabulary[0].lemma, "なめる")
        self.assertEqual(response.grammar_patterns[0].name, "〜てしまう")
        self.assertEqual(response.tokens[0].surface, "なめて")

    def test_local_analysis_returns_tokens_and_grammar(self):
        """本地分析返回 tokens 和 grammar_patterns，analysis 为 None"""
        from app.core.tokenizer import MeCabTokenizer
        from app.core.grammar_engine_optimized import GrammarRuleEngine
        from app.core.vocabulary import VocabularyLevelMapper

        tokenizer = MeCabTokenizer()
        grammar_engine = GrammarRuleEngine(rules_file="data/grammar_rules_complete.json")
        vocab = VocabularyLevelMapper(vocabulary_file="data/vocabulary_levels.json")

        service = AnalysisService(
            tokenizer=tokenizer,
            grammar_engine=grammar_engine,
            vocabulary_mapper=vocab,
        )

        response = service.analyze_local("行かなければなりません", "zh")

        self.assertEqual(response.sentence, "行かなければなりません")
        self.assertIsNone(response.analysis)
        self.assertGreater(len(response.tokens), 0)
        # 验证 token 被词汇表 enriched
        enriched = [t for t in response.tokens if t.jlpt_level]
        self.assertGreater(len(enriched), 0)


if __name__ == "__main__":
    unittest.main()
