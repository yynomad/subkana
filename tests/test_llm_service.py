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
    def test_llm_analysis_is_returned_with_legacy_fields(self):
        service = AnalysisService(FakeLLMClient())

        response = service.analyze("なめてしまいました", "zh")

        self.assertEqual(response.target_language, "zh")
        self.assertEqual(response.analysis.translation.text, "低估了对手。")
        self.assertEqual(response.analysis.sentence_patterns[0].name, "〜てしまう")
        self.assertEqual(response.analysis.vocabulary[0].lemma, "なめる")
        self.assertEqual(response.grammar_patterns[0].name, "〜てしまう")
        self.assertEqual(response.tokens[0].surface, "なめて")


if __name__ == "__main__":
    unittest.main()
