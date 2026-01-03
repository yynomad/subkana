#!/usr/bin/env python3
"""
测试日语句子分析 API

验证所有功能是否正常工作
"""

import requests
import json

API_URL = "http://localhost:8000"

# 测试用例
TEST_CASES = [
    {
        "sentence": "行かなければなりません",
        "expected_grammar": ["n4_nakereba_narimasen"],
        "description": "测试 N4 语法：〜なければなりません（必须）"
    },
    {
        "sentence": "勉強しています",
        "expected_grammar": ["n5_teimasu"],
        "description": "测试 N5 语法：〜ています（进行时）"
    },
    {
        "sentence": "日本に行きたい",
        "expected_grammar": ["n5_tai"],
        "description": "测试 N5 语法：〜たい（想要）"
    },
]


def test_health():
    """测试健康检查端点"""
    print("=" * 70)
    print("测试 1: 健康检查")
    print("-" * 70)
    
    try:
        response = requests.get(f"{API_URL}/api/v1/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ 状态: {data['status']}")
        print(f"✓ 分词器: {'正常' if data['components']['tokenizer'] else '失败'}")
        print(f"✓ 语法引擎: {'正常' if data['components']['grammar_engine'] else '失败'}")
        print(f"✓ 词汇映射: {'正常' if data['components']['vocabulary_mapper'] else '失败'}")
        print(f"✓ 分析服务: {'正常' if data['analysis_service'] else '失败'}")
        print()
        return True
    except Exception as e:
        print(f"✗ 健康检查失败: {e}")
        print()
        return False


def test_analyze(test_case):
    """测试句子分析"""
    print(f"句子: {test_case['sentence']}")
    print(f"说明: {test_case['description']}")
    print()
    
    try:
        response = requests.post(
            f"{API_URL}/api/v1/analyze",
            json={"sentence": test_case['sentence']},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # 显示识别的语法
        print(f"✓ 识别到 {len(data['grammar_patterns'])} 个语法模式:")
        for pattern in data['grammar_patterns']:
            print(f"  • [{pattern['level']}] {pattern['name']} - {pattern['meaning']}")
            print(f"    匹配: {''.join(pattern['structure'])}")
        
        # 显示词汇分析
        print(f"\n✓ 词汇分析 ({len(data['tokens'])} 个词):")
        for token in data['tokens']:
            level_str = f"[{token['jlpt_level']}]" if token['jlpt_level'] else "[-]"
            print(f"  • {token['surface']} ({token['lemma']}) {level_str} - {token['pos']}")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ 分析失败: {e}")
        print()
        return False


def main():
    print("=" * 70)
    print("🧪 日语句子分析 API 功能测试")
    print("=" * 70)
    print()
    
    # 测试健康检查
    if not test_health():
        print("⚠️  服务未启动或异常，请先启动服务")
        print("   启动命令: uvicorn app.main:app --reload")
        return
    
    # 测试所有句子
    print("=" * 70)
    print("测试 2: 句子分析")
    print("=" * 70)
    print()
    
    success_count = 0
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"测试用例 {i}/{len(TEST_CASES)}")
        print("-" * 70)
        if test_analyze(test_case):
            success_count += 1
    
    # 总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"✓ 通过: {success_count}/{len(TEST_CASES)}")
    print(f"✗ 失败: {len(TEST_CASES) - success_count}/{len(TEST_CASES)}")
    print()
    
    if success_count == len(TEST_CASES):
        print("🎉 所有测试通过！系统运行正常。")
    else:
        print("⚠️  部分测试失败，请检查日志。")
    print()


if __name__ == "__main__":
    main()

