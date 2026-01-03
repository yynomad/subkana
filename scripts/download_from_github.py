#!/usr/bin/env python3
"""
从 GitHub 下载 JLPT 数据并转换为项目格式

数据源：
1. Bluskyo/JLPT_Vocabulary - 词汇数据（JSON格式）
2. 其他 GitHub 资源
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import time

# GitHub 数据源
BLUSKYO_REPO = "Bluskyo/JLPT_Vocabulary"
BLUSKYO_BASE_URL = "https://raw.githubusercontent.com/Bluskyo/JLPT_Vocabulary/master/data"

# 其他可能的资源
JAMSINCLAIR_REPO = "jamsinclair/open-anki-jlpt-decks"


def download_file(url: str, retry: int = 3) -> Optional[dict]:
    """下载 JSON 文件"""
    for attempt in range(retry):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < retry - 1:
                print(f"⚠️  重试 ({attempt + 1}/{retry})...")
                time.sleep(2)
            else:
                print(f"❌ 下载失败: {e}")
                return None
    return None


def download_bluskyo_vocabulary() -> Dict[str, str]:
    """从 Bluskyo 仓库下载所有级别的词汇"""
    print("📥 正在从 Bluskyo/JLPT_Vocabulary 下载词汇数据...")
    print("-" * 60)
    
    all_vocab = {}
    
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        url = f"{BLUSKYO_BASE_URL}/{level}.json"
        print(f"  下载 {level}...", end=" ")
        
        data = download_file(url)
        if data:
            # Bluskyo 格式可能是列表或字典
            if isinstance(data, list):
                for item in data:
                    # 尝试多种可能的字段名
                    word = (item.get('word') or item.get('kanji') or 
                           item.get('kana') or item.get('vocabulary'))
                    if word:
                        all_vocab[word] = level
            elif isinstance(data, dict):
                # 如果是字典，可能键就是词汇
                for word in data.keys():
                    all_vocab[word] = level
            
            count = len(data) if isinstance(data, list) else len(data) if isinstance(data, dict) else 0
            print(f"✅ {count} 词")
        else:
            print("❌ 失败")
        
        time.sleep(0.5)  # 避免请求过快
    
    return all_vocab


def download_grammar_from_hanabira() -> List[Dict]:
    """尝试从 Hanabira 下载语法数据"""
    print("📥 正在尝试从 Hanabira.org 下载语法数据...")
    print("-" * 60)
    
    # 尝试多个可能的端点
    endpoints = [
        "https://hanabira.org/api/grammar",
        "https://www.hanabira.org/api/grammar",
        "https://hanabira.org/downloads/grammar.json",
    ]
    
    for endpoint in endpoints:
        print(f"  尝试 {endpoint}...", end=" ")
        data = download_file(endpoint)
        if data:
            print("✅ 成功")
            return data if isinstance(data, list) else []
        print("❌ 失败")
        time.sleep(1)
    
    return []


def convert_grammar_to_format(raw_grammar: List[Dict]) -> List[Dict]:
    """将原始语法数据转换为项目格式"""
    converted = []
    
    for idx, item in enumerate(raw_grammar):
        # 提取字段（根据实际数据调整）
        grammar_id = (item.get('id') or item.get('grammar_id') or 
                     f"grammar_{idx}")
        name = (item.get('name') or item.get('pattern') or 
               item.get('grammar_point') or "")
        level = (item.get('level') or item.get('jlpt_level') or "").upper()
        meaning = (item.get('meaning') or item.get('translation') or 
                  item.get('explanation') or "")
        
        # 构建 pattern（需要根据实际数据结构调整）
        # 这里提供一个基础框架，实际需要根据数据源调整
        pattern = item.get('pattern', [])
        if not pattern:
            # 如果没有现成的 pattern，尝试从其他字段构建
            structure = item.get('structure', '')
            if structure:
                # 这里需要根据实际格式解析
                pattern = [{"pos": "動詞"}]  # 占位符
        
        converted.append({
            "id": str(grammar_id),
            "name": str(name),
            "level": str(level),
            "meaning": str(meaning),
            "pattern": pattern if pattern else [{"pos": "動詞"}]
        })
    
    return converted


def merge_vocabulary(existing: Dict[str, str], new: Dict[str, str]) -> Dict[str, str]:
    """合并词汇字典（新数据优先）"""
    merged = existing.copy()
    merged.update(new)
    return dict(sorted(merged.items()))


def save_json(data: any, filepath: Path):
    """保存 JSON 文件"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 从 GitHub 下载 JLPT 数据")
    print("=" * 60)
    print()
    
    # 输出路径
    vocab_output = Path(__file__).parent.parent / "data" / "vocabulary_levels.json"
    grammar_output = Path(__file__).parent.parent / "data" / "grammar_rules.json"
    
    # 1. 下载词汇数据
    print("📚 下载词汇数据")
    print("=" * 60)
    
    new_vocab = download_bluskyo_vocabulary()
    
    # 合并已有数据
    existing_vocab = {}
    if vocab_output.exists():
        try:
            with open(vocab_output, 'r', encoding='utf-8') as f:
                existing_vocab = json.load(f)
        except:
            pass
    
    if new_vocab:
        merged_vocab = merge_vocabulary(existing_vocab, new_vocab)
        save_json(merged_vocab, vocab_output)
        print(f"\n✅ 词汇数据已保存: {len(merged_vocab)} 个词汇")
    else:
        print("\n⚠️  未下载到新的词汇数据")
    
    # 2. 下载语法数据
    print()
    print("📚 下载语法数据")
    print("=" * 60)
    
    raw_grammar = download_grammar_from_hanabira()
    
    if raw_grammar:
        converted_grammar = convert_grammar_to_format(raw_grammar)
        save_json(converted_grammar, grammar_output)
        print(f"\n✅ 语法数据已保存: {len(converted_grammar)} 条规则")
    else:
        print("\n⚠️  未下载到语法数据")
        print("💡 提示: 语法数据可能需要手动整理或从其他来源获取")
    
    # 打印统计
    print()
    print("=" * 60)
    print("📊 数据统计")
    print("=" * 60)
    
    if vocab_output.exists():
        with open(vocab_output, 'r', encoding='utf-8') as f:
            vocab = json.load(f)
        levels = {}
        for level in vocab.values():
            levels[level] = levels.get(level, 0) + 1
        print(f"词汇总数: {len(vocab)}")
        for level in ["N5", "N4", "N3", "N2", "N1"]:
            print(f"  {level}: {levels.get(level, 0)} 词")
    
    if grammar_output.exists():
        with open(grammar_output, 'r', encoding='utf-8') as f:
            grammar = json.load(f)
        levels = {}
        for rule in grammar:
            level = rule.get('level', '')
            levels[level] = levels.get(level, 0) + 1
        print(f"语法规则总数: {len(grammar)}")
        for level in ["N5", "N4", "N3", "N2", "N1"]:
            print(f"  {level}: {levels.get(level, 0)} 条")
    
    print()
    print("✅ 完成！")


if __name__ == "__main__":
    main()

