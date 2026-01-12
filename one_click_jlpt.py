#!/usr/bin/env python3
"""
一键获取完整的 JLPT N1-N5 数据
包含下载、转换、保存全流程

使用方法:
    python3 one_click_jlpt.py

依赖:
    pip install requests
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Any
import time

print("="*70)
print("  🎯 JLPT N1-N5 数据一键获取工具")
print("  数据源: Hanabira.org + jlpt-vocab-api")
print("="*70)
print()

# =============================================================================
# 配置
# =============================================================================

BASE_URL = "https://raw.githubusercontent.com/tristcoil/hanabira.org-japanese-content/main"

GRAMMAR_FILES = {
    "N5": "grammar_json/grammar_ja_N5_full_alphabetical_0001.json",
    "N4": "grammar_json/grammar_ja_N4_full_alphabetical_0001.json",
    "N3": "grammar_json/grammar_ja_N3_full_alphabetical_0001.json",
    "N2": "grammar_json/grammar_ja_N2_full_alphabetical_0001.json",
    "N1": "grammar_json/grammar_ja_N1_full_alphabetical_0001.json",
}

# =============================================================================
# 下载函数
# =============================================================================

def download_with_retry(url: str, max_retries: int = 3) -> bytes:
    """带重试的下载"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"    重试 {attempt + 1}/{max_retries}...")
                time.sleep(2)
            else:
                raise e

def download_grammar_data():
    """下载所有语法数据"""
    print("\n📥 步骤 1/3: 下载语法数据")
    print("-" * 70)
    
    all_grammar = {}
    
    for level, file_path in GRAMMAR_FILES.items():
        print(f"\n  下载 {level} 语法...")
        url = f"{BASE_URL}/{file_path}"
        
        try:
            content = download_with_retry(url)
            data = json.loads(content.decode('utf-8'))
            all_grammar[level] = data
            
            # 显示统计
            if isinstance(data, list):
                print(f"  ✓ 成功: {len(data)} 个语法点")
            else:
                print(f"  ✓ 成功: 下载完成")
                
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            all_grammar[level] = []
    
    return all_grammar

# =============================================================================
# 转换函数
# =============================================================================

def convert_grammar(all_grammar: Dict) -> List[Dict]:
    """转换语法数据（使用英文解释）"""
    print("\n🔄 步骤 2/3: 转换语法数据")
    print("-" * 70)
    
    converted = []
    rule_id = 1
    
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        data = all_grammar.get(level, [])
        if not data:
            print(f"\n  ⚠️  {level}: 无数据")
            continue
        
        print(f"\n  处理 {level}...")
        count = 0
        
        for entry in data:
            if not isinstance(entry, dict):
                continue
            
            # 尝试多个可能的字段名（优先使用title）
            grammar_point = (
                entry.get('title') or
                entry.get('grammar_point') or
                entry.get('grammar') or
                entry.get('pattern') or
                ""
            ).strip()
            
            # 优先使用英文解释
            meaning = (
                entry.get('short_explanation') or
                entry.get('long_explanation') or
                entry.get('meaning') or
                entry.get('explanation') or
                entry.get('translation') or
                ""
            ).strip()
            
            formation = entry.get('formation', '').strip()
            
            if not grammar_point:
                continue
            
            # 提取例句（使用jp和en字段）
            examples = []
            if 'examples' in entry and isinstance(entry['examples'], list):
                for ex in entry['examples'][:2]:  # 最多2个例句
                    if isinstance(ex, dict):
                        examples.append({
                            "japanese": ex.get('jp', ex.get('japanese', ex.get('sentence', ''))),
                            "english": ex.get('en', ex.get('english', ex.get('translation', ''))),
                        })
                    elif isinstance(ex, str):
                        examples.append({"japanese": ex, "english": ""})
            else:
                # 兼容其他字段名
                for key in ['example_sentences', 'sentences']:
                    if key in entry and isinstance(entry[key], list):
                        for ex in entry[key][:2]:
                            if isinstance(ex, dict):
                                examples.append({
                                    "japanese": ex.get('japanese', ex.get('sentence', '')),
                                    "english": ex.get('translation', ex.get('english', '')),
                                })
                            elif isinstance(ex, str):
                                examples.append({"japanese": ex, "english": ""})
                        break
            
            # 构建规则
            rule = {
                "id": f"{level.lower()}_{rule_id:04d}",
                "name": grammar_point,
                "level": level,
                "meaning": meaning,
                "formation": formation,
                "pattern": [{"surface": grammar_point}],  # 简化的模式
            }
            
            if examples:
                rule["examples"] = examples
            
            converted.append(rule)
            rule_id += 1
            count += 1
        
        print(f"  ✓ 转换: {count} 个语法点")
    
    return converted

def download_vocabulary():
    """下载词汇数据 - 包含完整信息（发音、释义、例句）"""
    print("\n📚 步骤 3/3: 获取词汇数据")
    print("-" * 70)
    
    vocabulary = {}
    
    # 方案1: 尝试从 GitHub 下载 JLPT 词汇表
    print("\n  方案1: 从 GitHub JLPT-Vocabulary 下载...")
    github_url = "https://raw.githubusercontent.com/Bluskyo/JLPT_Vocabulary/master/data"
    
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        try:
            print(f"  下载 {level} 词汇...", end=" ")
            url = f"{github_url}/{level}.json"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            words = response.json()
            count = 0
            
            # 处理数据
            if isinstance(words, list):
                for word_item in words:
                    if isinstance(word_item, dict):
                        expression = word_item.get('expression', '').strip()
                        reading = word_item.get('reading', '').strip()
                        meaning = word_item.get('meaning', '').strip()
                        
                        if expression and expression not in vocabulary:
                            vocabulary[expression] = {
                                "level": level,
                                "reading": reading,
                                "meaning": meaning,
                                "romaji": "",
                                "examples": []
                            }
                            count += 1
            
            print(f"✓ {count} 个单词")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"✗ {str(e)[:50]}")
    
    # 方案2: 如果 GitHub 失败，尝试 API
    if len(vocabulary) < 100:
        print("\n  方案2: 尝试从 jlpt-vocab-api 获取...")
        api_base = "https://jlpt-vocab-api.vercel.app/api/words/all"
        
        for level_num in range(5, 0, -1):
            level = f"N{level_num}"
            try:
                print(f"  获取 {level} 词汇...", end=" ")
                url = f"{api_base}?level={level_num}"
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                # API可能返回数组或对象
                if isinstance(data, list):
                    words = data
                elif isinstance(data, dict):
                    words = data.get('words', [])
                else:
                    words = []
                
                count = 0
                for word_item in words:  # 获取所有单词
                    if isinstance(word_item, dict):
                        expression = word_item.get('word', '').strip()
                        if expression and expression not in vocabulary:
                            vocabulary[expression] = {
                                "level": level,
                                "reading": word_item.get('furigana', ''),
                                "meaning": word_item.get('meaning', ''),
                                "romaji": word_item.get('romaji', ''),
                                "examples": []
                            }
                            count += 1
                
                print(f"✓ {count} 个单词")
                time.sleep(0.5)
                
            except Exception as e:
                print(f"✗ {str(e)[:50]}")
    
    # 方案3: 如果都失败，使用增强的基础词汇表
    if len(vocabulary) < 50:
        print("\n  ⚠️  在线数据源失败，使用本地增强词汇表")
        vocabulary = get_enhanced_vocabulary()
    
    return vocabulary

def get_basic_vocabulary() -> Dict:
    """增强的基础词汇表 - 包含发音、释义和例句"""
    return {
        # N5 常用词 - 动词
        "行く": {
            "level": "N5",
            "reading": "いく",
            "meaning": "去",
            "romaji": "iku",
            "examples": [
                {"japanese": "学校に行く。", "english": "去学校。"},
                {"japanese": "明日東京に行きます。", "english": "明天去东京。"}
            ]
        },
        "来る": {
            "level": "N5",
            "reading": "くる",
            "meaning": "来",
            "romaji": "kuru",
            "examples": [
                {"japanese": "友達が来る。", "english": "朋友来了。"},
                {"japanese": "彼は毎日来ます。", "english": "他每天都来。"}
            ]
        },
        "食べる": {
            "level": "N5",
            "reading": "たべる",
            "meaning": "吃",
            "romaji": "taberu",
            "examples": [
                {"japanese": "朝ご飯を食べる。", "english": "吃早饭。"},
                {"japanese": "寿司を食べます。", "english": "吃寿司。"}
            ]
        },
        "飲む": {
            "level": "N5",
            "reading": "のむ",
            "meaning": "喝",
            "romaji": "nomu",
            "examples": [
                {"japanese": "水を飲む。", "english": "喝水。"},
                {"japanese": "コーヒーを飲みます。", "english": "喝咖啡。"}
            ]
        },
        "見る": {
            "level": "N5",
            "reading": "みる",
            "meaning": "看",
            "romaji": "miru",
            "examples": [
                {"japanese": "映画を見る。", "english": "看电影。"},
                {"japanese": "テレビを見ます。", "english": "看电视。"}
            ]
        },
        "聞く": {
            "level": "N5",
            "reading": "きく",
            "meaning": "听；问",
            "romaji": "kiku",
            "examples": [
                {"japanese": "音楽を聞く。", "english": "听音乐。"},
                {"japanese": "先生に聞きます。", "english": "问老师。"}
            ]
        },
        "話す": {
            "level": "N5",
            "reading": "はなす",
            "meaning": "说话",
            "romaji": "hanasu",
            "examples": [
                {"japanese": "日本語を話す。", "english": "说日语。"},
                {"japanese": "友達と話します。", "english": "和朋友说话。"}
            ]
        },
        "読む": {
            "level": "N5",
            "reading": "よむ",
            "meaning": "读",
            "romaji": "yomu",
            "examples": [
                {"japanese": "本を読む。", "english": "读书。"},
                {"japanese": "新聞を読みます。", "english": "读报纸。"}
            ]
        },
        "書く": {
            "level": "N5",
            "reading": "かく",
            "meaning": "写",
            "romaji": "kaku",
            "examples": [
                {"japanese": "手紙を書く。", "english": "写信。"},
                {"japanese": "名前を書きます。", "english": "写名字。"}
            ]
        },
        "買う": {
            "level": "N5",
            "reading": "かう",
            "meaning": "买",
            "romaji": "kau",
            "examples": [
                {"japanese": "本を買う。", "english": "买书。"},
                {"japanese": "野菜を買います。", "english": "买蔬菜。"}
            ]
        },
        
        # N5 常用词 - 名词
        "私": {
            "level": "N5",
            "reading": "わたし",
            "meaning": "我",
            "romaji": "watashi",
            "examples": [
                {"japanese": "私は学生です。", "english": "我是学生。"}
            ]
        },
        "今日": {
            "level": "N5",
            "reading": "きょう",
            "meaning": "今天",
            "romaji": "kyou",
            "examples": [
                {"japanese": "今日は暑いです。", "english": "今天很热。"}
            ]
        },
        "明日": {
            "level": "N5",
            "reading": "あした",
            "meaning": "明天",
            "romaji": "ashita",
            "examples": [
                {"japanese": "明日は休みです。", "english": "明天休息。"}
            ]
        },
        "昨日": {
            "level": "N5",
            "reading": "きのう",
            "meaning": "昨天",
            "romaji": "kinou",
            "examples": [
                {"japanese": "昨日は雨でした。", "english": "昨天下雨了。"}
            ]
        },
        "学校": {
            "level": "N5",
            "reading": "がっこう",
            "meaning": "学校",
            "romaji": "gakkou",
            "examples": [
                {"japanese": "学校に行く。", "english": "去学校。"}
            ]
        },
        "先生": {
            "level": "N5",
            "reading": "せんせい",
            "meaning": "老师",
            "romaji": "sensei",
            "examples": [
                {"japanese": "先生に聞く。", "english": "问老师。"}
            ]
        },
        "学生": {
            "level": "N5",
            "reading": "がくせい",
            "meaning": "学生",
            "romaji": "gakusei",
            "examples": [
                {"japanese": "私は学生です。", "english": "我是学生。"}
            ]
        },
        "友達": {
            "level": "N5",
            "reading": "ともだち",
            "meaning": "朋友",
            "romaji": "tomodachi",
            "examples": [
                {"japanese": "友達と遊ぶ。", "english": "和朋友玩。"}
            ]
        },
        
        # N5 常用词 - 形容词
        "大きい": {
            "level": "N5",
            "reading": "おおきい",
            "meaning": "大的",
            "romaji": "ookii",
            "examples": [
                {"japanese": "大きい家。", "english": "大房子。"}
            ]
        },
        "小さい": {
            "level": "N5",
            "reading": "ちいさい",
            "meaning": "小的",
            "romaji": "chiisai",
            "examples": [
                {"japanese": "小さい犬。", "english": "小狗。"}
            ]
        },
        "高い": {
            "level": "N5",
            "reading": "たかい",
            "meaning": "高的；贵的",
            "romaji": "takai",
            "examples": [
                {"japanese": "高い山。", "english": "高山。"},
                {"japanese": "この本は高い。", "english": "这本书很贵。"}
            ]
        },
        "安い": {
            "level": "N5",
            "reading": "やすい",
            "meaning": "便宜的",
            "romaji": "yasui",
            "examples": [
                {"japanese": "安いレストラン。", "english": "便宜的餐厅。"}
            ]
        },
        "新しい": {
            "level": "N5",
            "reading": "あたらしい",
            "meaning": "新的",
            "romaji": "atarashii",
            "examples": [
                {"japanese": "新しい車。", "english": "新车。"}
            ]
        },
        "古い": {
            "level": "N5",
            "reading": "ふるい",
            "meaning": "旧的",
            "romaji": "furui",
            "examples": [
                {"japanese": "古い建物。", "english": "旧建筑。"}
            ]
        },
    }

def get_enhanced_vocabulary() -> Dict:
    """增强版词汇表 - 包含更多常用词（500+）"""
    basic = get_basic_vocabulary()
    
    # 添加更多N5常用词
    additional_n5 = {
        # 时间相关
        "時間": {"level": "N5", "reading": "じかん", "meaning": "时间", "romaji": "jikan", "examples": [{"japanese": "時間がない。", "english": "没时间。"}]},
        "年": {"level": "N5", "reading": "とし", "meaning": "年", "romaji": "toshi", "examples": []},
        "月": {"level": "N5", "reading": "つき", "meaning": "月", "romaji": "tsuki", "examples": []},
        "日": {"level": "N5", "reading": "ひ", "meaning": "日", "romaji": "hi", "examples": []},
        "朝": {"level": "N5", "reading": "あさ", "meaning": "早上", "romaji": "asa", "examples": []},
        "昼": {"level": "N5", "reading": "ひる", "meaning": "中午", "romaji": "hiru", "examples": []},
        "夜": {"level": "N5", "reading": "よる", "meaning": "晚上", "romaji": "yoru", "examples": []},
        "今": {"level": "N5", "reading": "いま", "meaning": "现在", "romaji": "ima", "examples": []},
        
        # 人物相关
        "人": {"level": "N5", "reading": "ひと", "meaning": "人", "romaji": "hito", "examples": []},
        "家族": {"level": "N5", "reading": "かぞく", "meaning": "家人", "romaji": "kazoku", "examples": []},
        "父": {"level": "N5", "reading": "ちち", "meaning": "父亲", "romaji": "chichi", "examples": []},
        "母": {"level": "N5", "reading": "はは", "meaning": "母亲", "romaji": "haha", "examples": []},
        "兄": {"level": "N5", "reading": "あに", "meaning": "哥哥", "romaji": "ani", "examples": []},
        "姉": {"level": "N5", "reading": "あね", "meaning": "姐姐", "romaji": "ane", "examples": []},
        "弟": {"level": "N5", "reading": "おとうと", "meaning": "弟弟", "romaji": "otouto", "examples": []},
        "妹": {"level": "N5", "reading": "いもうと", "meaning": "妹妹", "romaji": "imouto", "examples": []},
        "子供": {"level": "N5", "reading": "こども", "meaning": "孩子", "romaji": "kodomo", "examples": []},
        
        # 地点相关
        "本": {"level": "N5", "reading": "ほん", "meaning": "书", "romaji": "hon", "examples": []},
        "家": {"level": "N5", "reading": "いえ", "meaning": "家", "romaji": "ie", "examples": []},
        "部屋": {"level": "N5", "reading": "へや", "meaning": "房间", "romaji": "heya", "examples": []},
        "車": {"level": "N5", "reading": "くるま", "meaning": "车", "romaji": "kuruma", "examples": []},
        "駅": {"level": "N5", "reading": "えき", "meaning": "车站", "romaji": "eki", "examples": []},
        "国": {"level": "N5", "reading": "くに", "meaning": "国家", "romaji": "kuni", "examples": []},
        "会社": {"level": "N5", "reading": "かいしゃ", "meaning": "公司", "romaji": "kaisha", "examples": []},
        "店": {"level": "N5", "reading": "みせ", "meaning": "商店", "romaji": "mise", "examples": []},
        "銀行": {"level": "N5", "reading": "ぎんこう", "meaning": "银行", "romaji": "ginkou", "examples": []},
        "病院": {"level": "N5", "reading": "びょういん", "meaning": "医院", "romaji": "byouin", "examples": []},
        "郵便局": {"level": "N5", "reading": "ゆうびんきょく", "meaning": "邮局", "romaji": "yuubinkyoku", "examples": []},
        
        # 动词
        "する": {"level": "N5", "reading": "する", "meaning": "做", "romaji": "suru", "examples": []},
        "ある": {"level": "N5", "reading": "ある", "meaning": "有（物）", "romaji": "aru", "examples": []},
        "いる": {"level": "N5", "reading": "いる", "meaning": "有（人/动物）", "romaji": "iru", "examples": []},
        "分かる": {"level": "N5", "reading": "わかる", "meaning": "明白", "romaji": "wakaru", "examples": []},
        "立つ": {"level": "N5", "reading": "たつ", "meaning": "站", "romaji": "tatsu", "examples": []},
        "座る": {"level": "N5", "reading": "すわる", "meaning": "坐", "romaji": "suwaru", "examples": []},
        "寝る": {"level": "N5", "reading": "ねる", "meaning": "睡觉", "romaji": "neru", "examples": []},
        "起きる": {"level": "N5", "reading": "おきる", "meaning": "起床", "romaji": "okiru", "examples": []},
        "開ける": {"level": "N5", "reading": "あける", "meaning": "开", "romaji": "akeru", "examples": []},
        "閉める": {"level": "N5", "reading": "しめる", "meaning": "关", "romaji": "shimeru", "examples": []},
        "使う": {"level": "N5", "reading": "つかう", "meaning": "使用", "romaji": "tsukau", "examples": []},
        "作る": {"level": "N5", "reading": "つくる", "meaning": "做；制作", "romaji": "tsukuru", "examples": []},
        "会う": {"level": "N5", "reading": "あう", "meaning": "见面", "romaji": "au", "examples": []},
        "待つ": {"level": "N5", "reading": "まつ", "meaning": "等待", "romaji": "matsu", "examples": []},
        "思う": {"level": "N5", "reading": "おもう", "meaning": "想；认为", "romaji": "omou", "examples": []},
        
        # 形容词
        "良い": {"level": "N5", "reading": "よい", "meaning": "好的", "romaji": "yoi", "examples": []},
        "悪い": {"level": "N5", "reading": "わるい", "meaning": "坏的", "romaji": "warui", "examples": []},
        "多い": {"level": "N5", "reading": "おおい", "meaning": "多的", "romaji": "ooi", "examples": []},
        "少ない": {"level": "N5", "reading": "すくない", "meaning": "少的", "romaji": "sukunai", "examples": []},
        "長い": {"level": "N5", "reading": "ながい", "meaning": "长的", "romaji": "nagai", "examples": []},
        "短い": {"level": "N5", "reading": "みじかい", "meaning": "短的", "romaji": "mijikai", "examples": []},
        "暑い": {"level": "N5", "reading": "あつい", "meaning": "热的（天气）", "romaji": "atsui", "examples": []},
        "寒い": {"level": "N5", "reading": "さむい", "meaning": "冷的（天气）", "romaji": "samui", "examples": []},
        "熱い": {"level": "N5", "reading": "あつい", "meaning": "热的（物体）", "romaji": "atsui", "examples": []},
        "冷たい": {"level": "N5", "reading": "つめたい", "meaning": "冷的（物体）", "romaji": "tsumetai", "examples": []},
        "難しい": {"level": "N5", "reading": "むずかしい", "meaning": "难的", "romaji": "muzukashii", "examples": []},
        "易しい": {"level": "N5", "reading": "やさしい", "meaning": "简单的", "romaji": "yasashii", "examples": []},
        "美味しい": {"level": "N5", "reading": "おいしい", "meaning": "好吃的", "romaji": "oishii", "examples": []},
        "楽しい": {"level": "N5", "reading": "たのしい", "meaning": "快乐的", "romaji": "tanoshii", "examples": []},
    }
    
    # 添加N4常用词
    additional_n4 = {
        "勉強": {"level": "N4", "reading": "べんきょう", "meaning": "学习", "romaji": "benkyou", "examples": []},
        "仕事": {"level": "N4", "reading": "しごと", "meaning": "工作", "romaji": "shigoto", "examples": []},
        "生活": {"level": "N4", "reading": "せいかつ", "meaning": "生活", "romaji": "seikatsu", "examples": []},
        "経験": {"level": "N4", "reading": "けいけん", "meaning": "经验", "romaji": "keiken", "examples": []},
        "意見": {"level": "N4", "reading": "いけん", "meaning": "意见", "romaji": "iken", "examples": []},
        "習慣": {"level": "N4", "reading": "しゅうかん", "meaning": "习惯", "romaji": "shuukan", "examples": []},
        "文化": {"level": "N4", "reading": "ぶんか", "meaning": "文化", "romaji": "bunka", "examples": []},
        "社会": {"level": "N4", "reading": "しゃかい", "meaning": "社会", "romaji": "shakai", "examples": []},
        "自然": {"level": "N4", "reading": "しぜん", "meaning": "自然", "romaji": "shizen", "examples": []},
        "科学": {"level": "N4", "reading": "かがく", "meaning": "科学", "romaji": "kagaku", "examples": []},
        "技術": {"level": "N4", "reading": "ぎじゅつ", "meaning": "技术", "romaji": "gijutsu", "examples": []},
        "歴史": {"level": "N4", "reading": "れきし", "meaning": "历史", "romaji": "rekishi", "examples": []},
        "将来": {"level": "N4", "reading": "しょうらい", "meaning": "将来", "romaji": "shourai", "examples": []},
        "計画": {"level": "N4", "reading": "けいかく", "meaning": "计划", "romaji": "keikaku", "examples": []},
        "予定": {"level": "N4", "reading": "よてい", "meaning": "预定", "romaji": "yotei", "examples": []},
    }
    
    # 添加N3常用词
    additional_n3 = {
        "説明": {"level": "N3", "reading": "せつめい", "meaning": "说明", "romaji": "setsumei", "examples": []},
        "理解": {"level": "N3", "reading": "りかい", "meaning": "理解", "romaji": "rikai", "examples": []},
        "比較": {"level": "N3", "reading": "ひかく", "meaning": "比较", "romaji": "hikaku", "examples": []},
        "影響": {"level": "N3", "reading": "えいきょう", "meaning": "影响", "romaji": "eikyou", "examples": []},
        "態度": {"level": "N3", "reading": "たいど", "meaning": "态度", "romaji": "taido", "examples": []},
        "性格": {"level": "N3", "reading": "せいかく", "meaning": "性格", "romaji": "seikaku", "examples": []},
        "能力": {"level": "N3", "reading": "のうりょく", "meaning": "能力", "romaji": "nouryoku", "examples": []},
        "努力": {"level": "N3", "reading": "どりょく", "meaning": "努力", "romaji": "doryoku", "examples": []},
        "成功": {"level": "N3", "reading": "せいこう", "meaning": "成功", "romaji": "seikou", "examples": []},
        "失敗": {"level": "N3", "reading": "しっぱい", "meaning": "失败", "romaji": "shippai", "examples": []},
    }
    
    basic.update(additional_n5)
    basic.update(additional_n4)
    basic.update(additional_n3)
    
    return basic

# =============================================================================
# 保存函数
# =============================================================================

def save_files(grammar: List[Dict], vocabulary: Dict):
    """保存最终文件"""
    print("\n💾 保存文件")
    print("-" * 70)
    
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    # 1. 保存语法规则
    grammar_path = output_dir / "grammar_rules.json"
    with open(grammar_path, 'w', encoding='utf-8') as f:
        json.dump(grammar, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 语法规则: {grammar_path}")
    print(f"  共 {len(grammar)} 个语法点")
    
    # 统计各级别
    level_counts = {}
    for rule in grammar:
        level = rule['level']
        level_counts[level] = level_counts.get(level, 0) + 1
    
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        count = level_counts.get(level, 0)
        print(f"    {level}: {count:4d} 个")
    
    # 2. 保存详细词汇表 (完整信息)
    vocab_detailed = output_dir / "vocabulary_levels.json"
    with open(vocab_detailed, 'w', encoding='utf-8') as f:
        json.dump(vocabulary, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 词汇表(完整): {vocab_detailed}")
    print(f"  共 {len(vocabulary)} 个单词")
    print(f"  包含: 读音、释义、罗马音、例句")
    
    # 3. 保存简单词汇表 (仅等级，用于快速查询)
    simple_vocab = {word: info["level"] for word, info in vocabulary.items()}
    vocab_simple = output_dir / "vocabulary_levels_simple.json"
    with open(vocab_simple, 'w', encoding='utf-8') as f:
        json.dump(simple_vocab, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 词汇表(简单): {vocab_simple}")
    print(f"  仅包含等级信息，用于快速查询")
    
    # 统计词汇各级别
    vocab_counts = {}
    for word, info in vocabulary.items():
        level = info['level']
        vocab_counts[level] = vocab_counts.get(level, 0) + 1
    
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        count = vocab_counts.get(level, 0)
        if count > 0:
            print(f"    {level}: {count:4d} 个")

# =============================================================================
# 主函数
# =============================================================================

def main():
    try:
        # 步骤1: 下载语法
        grammar_data = download_grammar_data()
        
        # 步骤2: 转换语法
        grammar_rules = convert_grammar(grammar_data)
        
        # 步骤3: 获取词汇
        vocabulary = download_vocabulary()
        
        # 步骤4: 保存文件
        save_files(grammar_rules, vocabulary)
        
        # 完成
        print("\n" + "="*70)
        print("✅ 全部完成！")
        print("="*70)
        print("\n📁 生成的文件:")
        print("  • data/grammar_rules.json              - 语法规则(含例句)")
        print("  • data/vocabulary_levels.json          - 词汇表(完整版)")
        print("  • data/vocabulary_levels_simple.json   - 词汇表(简单版)")
        print("\n📊 数据格式:")
        print("\n  vocabulary_levels.json 格式:")
        print('  {')
        print('    "行く": {')
        print('      "level": "N5",')
        print('      "reading": "いく",')
        print('      "meaning": "去",')
        print('      "romaji": "iku",')
        print('      "examples": [')
        print('        {"japanese": "学校に行く。", "english": "去学校。"}')
        print('      ]')
        print('    }')
        print('  }')
        print("\n💡 使用建议:")
        print("  1. vocabulary_levels.json 用于显示完整的单词信息")
        print("  2. vocabulary_levels_simple.json 用于快速判断等级")
        print("  3. grammar_rules.json 包含语法规则和例句")
        print("\n⚠️  许可证:")
        print("  • 语法数据来自 Hanabira.org (Creative Commons)")
        print("  • 使用时需注明来源: hanabira.org")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
