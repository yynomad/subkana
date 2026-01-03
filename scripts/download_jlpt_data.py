#!/usr/bin/env python3
"""
从开源资源下载并转换 JLPT 数据

支持的数据源：
1. Hanabira.org - 完整的语法和词汇 JSON 数据集（推荐）
2. Bluskyo/JLPT_Vocabulary - GitHub 仓库的词汇数据
3. jamsinclair/open-anki-jlpt-decks - CSV 格式的词汇数据
"""

import json
import csv
import requests
from pathlib import Path
from typing import Dict, List, Optional
import time

# 数据源 URL
HANABIRA_GRAMMAR_URL = "https://hanabira.org/api/grammar"
HANABIRA_VOCAB_URL = "https://hanabira.org/api/vocabulary"
BLUSKYO_BASE_URL = "https://raw.githubusercontent.com/Bluskyo/JLPT_Vocabulary/master/data"
JAMSINCLAIR_BASE_URL = "https://raw.githubusercontent.com/jamsinclair/open-anki-jlpt-decks/master"


def download_from_hanabira_grammar() -> Optional[List[Dict]]:
    """从 Hanabira.org 下载语法数据"""
    print("📥 正在从 Hanabira.org 下载语法数据...")
    try:
        response = requests.get(HANABIRA_GRAMMAR_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✅ 成功下载 {len(data) if isinstance(data, list) else '未知数量'} 条语法规则")
        return data if isinstance(data, list) else None
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None


def download_from_hanabira_vocab() -> Optional[List[Dict]]:
    """从 Hanabira.org 下载词汇数据"""
    print("📥 正在从 Hanabira.org 下载词汇数据...")
    try:
        response = requests.get(HANABIRA_VOCAB_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✅ 成功下载 {len(data) if isinstance(data, list) else '未知数量'} 个词汇")
        return data if isinstance(data, list) else None
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None


def download_from_bluskyo(level: str) -> Optional[List[Dict]]:
    """从 Bluskyo/JLPT_Vocabulary 下载词汇数据"""
    url = f"{BLUSKYO_BASE_URL}/{level}.json"
    print(f"📥 正在从 Bluskyo 下载 {level} 词汇...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"✅ 成功下载 {len(data)} 个 {level} 词汇")
        return data
    except Exception as e:
        print(f"⚠️  下载 {level} 失败: {e}")
        return None


def convert_hanabira_grammar_to_format(hanabira_data: List[Dict]) -> List[Dict]:
    """将 Hanabira 语法数据转换为项目格式"""
    converted = []
    
    for item in hanabira_data:
        # 提取基本信息
        grammar_id = item.get('id', '')
        name = item.get('name', '')
        level = item.get('level', '').upper()
        meaning = item.get('meaning', '')
        
        # 构建 pattern（需要根据实际数据结构调整）
        # 这里是一个示例转换，实际需要根据 Hanabira 的数据结构调整
        pattern = []
        
        # 如果有结构信息，转换为 pattern
        structure = item.get('structure', '')
        if structure:
            # 这里需要根据实际数据结构解析
            # 暂时使用简化版本
            pattern = [
                {"pos": "動詞"}  # 占位符，需要根据实际数据调整
            ]
        
        converted.append({
            "id": grammar_id or f"hanabira_{len(converted)}",
            "name": name,
            "level": level,
            "meaning": meaning,
            "pattern": pattern
        })
    
    return converted


def convert_hanabira_vocab_to_format(hanabira_data: List[Dict]) -> Dict[str, str]:
    """将 Hanabira 词汇数据转换为项目格式"""
    vocab_dict = {}
    
    for item in hanabira_data:
        word = item.get('word', '') or item.get('kanji', '') or item.get('kana', '')
        level = item.get('level', '').upper()
        
        if word and level:
            vocab_dict[word] = level
    
    return vocab_dict


def convert_bluskyo_to_format(bluskyo_data: List[Dict], level: str) -> Dict[str, str]:
    """将 Bluskyo 词汇数据转换为项目格式"""
    vocab_dict = {}
    
    for item in bluskyo_data:
        # Bluskyo 格式可能是 {"word": "行く", "reading": "いく", ...}
        word = item.get('word') or item.get('kanji') or item.get('kana')
        if word:
            vocab_dict[word] = level
    
    return vocab_dict


def merge_vocabulary(*vocab_dicts: Dict[str, str]) -> Dict[str, str]:
    """合并多个词汇字典（后面的优先级更高）"""
    merged = {}
    for vocab_dict in vocab_dicts:
        if vocab_dict:
            merged.update(vocab_dict)
    return dict(sorted(merged.items()))


def save_vocabulary(vocab_dict: Dict[str, str], output_path: str):
    """保存词汇数据"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(vocab_dict, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存 {len(vocab_dict)} 个词汇到 {output_path}")


def save_grammar_rules(rules: List[Dict], output_path: str):
    """保存语法规则"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存 {len(rules)} 条语法规则到 {output_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 JLPT 数据下载工具")
    print("=" * 60)
    print()
    
    # 输出文件路径
    vocab_output = Path(__file__).parent.parent / "data" / "vocabulary_levels.json"
    grammar_output = Path(__file__).parent.parent / "data" / "grammar_rules.json"
    
    # 1. 尝试从 Hanabira.org 下载（推荐）
    print("📚 方案 1: 从 Hanabira.org 下载（推荐）")
    print("-" * 60)
    
    hanabira_vocab = download_from_hanabira_vocab()
    hanabira_grammar = download_from_hanabira_grammar()
    
    if hanabira_vocab:
        vocab_dict = convert_hanabira_vocab_to_format(hanabira_vocab)
        save_vocabulary(vocab_dict, str(vocab_output))
    
    if hanabira_grammar:
        grammar_rules = convert_hanabira_grammar_to_format(hanabira_grammar)
        save_grammar_rules(grammar_rules, str(grammar_output))
    
    # 2. 如果 Hanabira 失败，尝试从 Bluskyo 下载词汇
    if not hanabira_vocab:
        print()
        print("📚 方案 2: 从 Bluskyo/JLPT_Vocabulary 下载词汇")
        print("-" * 60)
        
        all_vocab = {}
        for level in ["N5", "N4", "N3", "N2", "N1"]:
            bluskyo_data = download_from_bluskyo(level)
            if bluskyo_data:
                level_vocab = convert_bluskyo_to_format(bluskyo_data, level)
                all_vocab.update(level_vocab)
            time.sleep(0.5)  # 避免请求过快
        
        if all_vocab:
            # 合并已有的词汇（如果有）
            existing_vocab = {}
            if vocab_output.exists():
                try:
                    with open(vocab_output, 'r', encoding='utf-8') as f:
                        existing_vocab = json.load(f)
                except:
                    pass
            
            merged_vocab = merge_vocabulary(existing_vocab, all_vocab)
            save_vocabulary(merged_vocab, str(vocab_output))
    
    # 打印统计信息
    print()
    print("=" * 60)
    print("📊 数据统计")
    print("=" * 60)
    
    if vocab_output.exists():
        with open(vocab_output, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
        n5 = sum(1 for v in vocab_data.values() if v == "N5")
        n4 = sum(1 for v in vocab_data.values() if v == "N4")
        n3 = sum(1 for v in vocab_data.values() if v == "N3")
        n2 = sum(1 for v in vocab_data.values() if v == "N2")
        n1 = sum(1 for v in vocab_data.values() if v == "N1")
        print(f"词汇总数: {len(vocab_data)}")
        print(f"  N5: {n5} 词")
        print(f"  N4: {n4} 词")
        print(f"  N3: {n3} 词")
        print(f"  N2: {n2} 词")
        print(f"  N1: {n1} 词")
    
    if grammar_output.exists():
        with open(grammar_output, 'r', encoding='utf-8') as f:
            grammar_data = json.load(f)
        n5 = sum(1 for r in grammar_data if r.get('level') == "N5")
        n4 = sum(1 for r in grammar_data if r.get('level') == "N4")
        n3 = sum(1 for r in grammar_data if r.get('level') == "N3")
        n2 = sum(1 for r in grammar_data if r.get('level') == "N2")
        n1 = sum(1 for r in grammar_data if r.get('level') == "N1")
        print(f"语法规则总数: {len(grammar_data)}")
        print(f"  N5: {n5} 条")
        print(f"  N4: {n4} 条")
        print(f"  N3: {n3} 条")
        print(f"  N2: {n2} 条")
        print(f"  N1: {n1} 条")
    
    print()
    print("✅ 完成！")


if __name__ == "__main__":
    main()

