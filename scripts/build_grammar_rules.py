#!/usr/bin/env python3
"""
构建日语句型规则数据库

基于 JLPT N5-N1 常用句型构建 grammar_rules.json
包含完整的 N5-N3 常用句型
"""

import json
from pathlib import Path

# JLPT 句型规则定义
GRAMMAR_RULES = [
    # ========================================================================
    # N5 句型 (基础句型) - 最常用的基础语法
    # ========================================================================
    
    # 动词敬体形式
    {
        "id": "n5_masu",
        "name": "〜ます",
        "level": "N5",
        "meaning": "动词敬体（礼貌形式）",
        "pattern": [
            {"pos": "動詞", "conj": "連用形"},
            {"lemma": "ます", "conj": "基本形"}
        ]
    },
    {
        "id": "n5_mashita",
        "name": "〜ました",
        "level": "N5",
        "meaning": "……了（过去敬体）",
        "pattern": [
            {"pos": "動詞", "conj": "連用形"},
            {"lemma": "ます", "conj": "連用形"},
            {"surface": "た"}
        ]
    },
    {
        "id": "n5_masen",
        "name": "〜ません",
        "level": "N5",
        "meaning": "不……（否定敬体）",
        "pattern": [
            {"pos": "動詞", "conj": "連用形"},
            {"lemma": "ます", "conj": "未然形"},
            {"lemma": "ん"}
        ]
    },
    {
        "id": "n5_masendeshita",
        "name": "〜ませんでした",
        "level": "N5",
        "meaning": "没有……（过去否定敬体）",
        "pattern": [
            {"pos": "動詞", "conj": "連用形"},
            {"lemma": "ます"},
            {"lemma": "ん"},
            {"lemma": "です"},
            {"surface": "た"}
        ]
    },
    
    # 进行时/状态持续
    {
        "id": "n5_teimasu",
        "name": "〜ています",
        "level": "N5",
        "meaning": "正在……；……着（状态持续）",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"lemma": "いる", "conj": "連用形"},
            {"lemma": "ます", "conj": "基本形"}
        ]
    },
    {
        "id": "n5_teiru",
        "name": "〜ている",
        "level": "N5",
        "meaning": "正在……；……着（状态持续）",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"lemma": "いる", "conj": "基本形"}
        ]
    },
    
    # 愿望表达
    {
        "id": "n5_tai",
        "name": "〜たい",
        "level": "N5",
        "meaning": "想……",
        "pattern": [
            {"pos": "動詞", "conj": "連用形"},
            {"lemma": "たい"}
        ]
    },
    {
        "id": "n5_taidesu",
        "name": "〜たいです",
        "level": "N5",
        "meaning": "想……（敬体）",
        "pattern": [
            {"pos": "動詞", "conj": "連用形"},
            {"lemma": "たい"},
            {"lemma": "です"}
        ]
    },
    
    # 确认/语气助词
    {
        "id": "n5_desune",
        "name": "〜ですね",
        "level": "N5",
        "meaning": "……呢（确认/共鸣语气）",
        "pattern": [
            {"lemma": "です", "conj": "基本形"},
            {"lemma": "ね"}
        ]
    },
    {
        "id": "n5_desuyo",
        "name": "〜ですよ",
        "level": "N5",
        "meaning": "……哦（强调/提醒语气）",
        "pattern": [
            {"lemma": "です", "conj": "基本形"},
            {"lemma": "よ"}
        ]
    },
    {
        "id": "n5_masune",
        "name": "〜ますね",
        "level": "N5",
        "meaning": "……呢（动词敬体+确认语气）",
        "pattern": [
            {"lemma": "ます", "conj": "基本形"},
            {"lemma": "ね"}
        ]
    },
    {
        "id": "n5_masuyo",
        "name": "〜ますよ",
        "level": "N5",
        "meaning": "……哦（动词敬体+强调语气）",
        "pattern": [
            {"lemma": "ます", "conj": "基本形"},
            {"lemma": "よ"}
        ]
    },
    
    # 存在表达
    {
        "id": "n5_ga_arimasu",
        "name": "〜があります",
        "level": "N5",
        "meaning": "有……（无生命物体）",
        "pattern": [
            {"pos": "名詞"},
            {"surface": "が"},
            {"lemma": "ある"},
            {"lemma": "ます"}
        ]
    },
    {
        "id": "n5_ga_imasu",
        "name": "〜がいます",
        "level": "N5",
        "meaning": "有……（有生命物体）",
        "pattern": [
            {"pos": "名詞"},
            {"surface": "が"},
            {"lemma": "いる"},
            {"lemma": "ます"}
        ]
    },
    
    # 形容词/名词谓语
    {
        "id": "n5_desu",
        "name": "〜です",
        "level": "N5",
        "meaning": "是……（判断/断定）",
        "pattern": [
            {"pos": "名詞"},
            {"lemma": "です"}
        ]
    },
    {
        "id": "n5_adj_desu",
        "name": "形容词〜です",
        "level": "N5",
        "meaning": "……的（形容词敬体）",
        "pattern": [
            {"pos": "形容詞"},
            {"lemma": "です"}
        ]
    },
    
    # ========================================================================
    # N4 句型 (初级句型)
    # ========================================================================
    
    # 〜くらい/ぐらい - 大约
    {
        "id": "n4_kurai",
        "name": "〜くらい/ぐらい",
        "level": "N4",
        "meaning": "大约……；……左右",
        "pattern": [
            {"pos": "名詞"},
            {"lemma": "くらい"}
        ]
    },
    
    # 必须
    {
        "id": "n4_nakereba_naranai",
        "name": "〜なければならない",
        "level": "N4",
        "meaning": "必须……",
        "pattern": [
            {"pos": "動詞", "conj": "未然形"},
            {"lemma": "ない"},
            {"surface": "ば"},
            {"lemma": "なる"},
            {"lemma": "ない"}
        ]
    },
    {
        "id": "n4_nakereba_narimasen",
        "name": "〜なければなりません",
        "level": "N4",
        "meaning": "必须……（敬语）",
        "pattern": [
            {"pos": "動詞", "conj": "未然形"},
            {"lemma": "ない"},
            {"surface": "ば"},
            {"lemma": "なる"},
            {"lemma": "ます"},
            {"lemma": "ん"}
        ]
    },
    {
        "id": "n4_nakutewa_ikenai",
        "name": "〜なくてはいけない",
        "level": "N4",
        "meaning": "必须……；不得不……",
        "pattern": [
            {"pos": "動詞", "conj": "未然形"},
            {"lemma": "ない"},
            {"pos": "助詞"},
            {"surface": "は"},
            {"lemma": "いける"},
            {"lemma": "ない"}
        ]
    },
    
    # 许可/禁止
    {
        "id": "n4_temo_ii",
        "name": "〜てもいい",
        "level": "N4",
        "meaning": "可以……；……也行",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"surface": "も"},
            {"lemma": "いい"}
        ]
    },
    {
        "id": "n4_tewa_ikenai",
        "name": "〜てはいけない",
        "level": "N4",
        "meaning": "不可以……；不能……",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"surface": "は"},
            {"lemma": "いける"},
            {"lemma": "ない"}
        ]
    },
    {
        "id": "n4_naide_kudasai",
        "name": "〜ないでください",
        "level": "N4",
        "meaning": "请不要……",
        "pattern": [
            {"pos": "動詞", "conj": "未然形"},
            {"lemma": "ない"},
            {"pos": "助詞"},
            {"lemma": "くださる"}
        ]
    },
    
    # 能力/可能
    {
        "id": "n4_koto_ga_dekiru",
        "name": "〜ことができる",
        "level": "N4",
        "meaning": "能够……；可以……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "こと"},
            {"surface": "が"},
            {"lemma": "できる"}
        ]
    },
    
    # 时间相关
    {
        "id": "n4_tokoro",
        "name": "〜ところ",
        "level": "N4",
        "meaning": "正要……；刚刚……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "ところ"}
        ]
    },
    {
        "id": "n4_mae_ni",
        "name": "〜前に",
        "level": "N4",
        "meaning": "在……之前",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "前"},
            {"surface": "に"}
        ]
    },
    {
        "id": "n4_ato_de",
        "name": "〜後で",
        "level": "N4",
        "meaning": "在……之后",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "後"},
            {"pos": "助詞"}
        ]
    },
    
    # 列举/并列
    {
        "id": "n4_tari_tari",
        "name": "〜たり〜たり",
        "level": "N4",
        "meaning": "又……又……；……之类的",
        "pattern": [
            {"pos": "動詞"},
            {"surface": "たり"}
        ]
    },
    
    # 推测/判断
    {
        "id": "n4_hazu",
        "name": "〜はず",
        "level": "N4",
        "meaning": "应该……；理应……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "はず"}
        ]
    },
    {
        "id": "n4_you",
        "name": "〜よう",
        "level": "N4",
        "meaning": "好像……；似乎……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "よう"}
        ]
    },
    {
        "id": "n4_rashii",
        "name": "〜らしい",
        "level": "N4",
        "meaning": "好像……；似乎……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "らしい"}
        ]
    },
    {
        "id": "n4_souda_hearsay",
        "name": "〜そうだ（传闻）",
        "level": "N4",
        "meaning": "听说……；据说……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "そう"},
            {"lemma": "だ"}
        ]
    },
    {
        "id": "n4_souda_appearance",
        "name": "〜そう（样态）",
        "level": "N4",
        "meaning": "看起来……；好像要……",
        "pattern": [
            {"pos": "動詞", "conj": "連用形"},
            {"lemma": "そう"}
        ]
    },
    
    # 条件
    {
        "id": "n4_tara",
        "name": "〜たら",
        "level": "N4",
        "meaning": "如果……；……的话",
        "pattern": [
            {"pos": "動詞"},
            {"surface": "たら"}
        ]
    },
    {
        "id": "n4_nara",
        "name": "〜なら",
        "level": "N4",
        "meaning": "如果是……；说到……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "なら"}
        ]
    },
    {
        "id": "n4_ba",
        "name": "〜ば",
        "level": "N4",
        "meaning": "如果……",
        "pattern": [
            {"pos": "動詞", "conj": "仮定形"},
            {"surface": "ば"}
        ]
    },
    
    # 授受表现
    {
        "id": "n4_te_ageru",
        "name": "〜てあげる",
        "level": "N4",
        "meaning": "为（别人）做……",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"lemma": "あげる"}
        ]
    },
    {
        "id": "n4_te_morau",
        "name": "〜てもらう",
        "level": "N4",
        "meaning": "请（别人）做……；得到……",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"lemma": "もらう"}
        ]
    },
    {
        "id": "n4_te_kureru",
        "name": "〜てくれる",
        "level": "N4",
        "meaning": "（别人）为我做……",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"lemma": "くれる"}
        ]
    },
    
    # 意志/劝诱
    {
        "id": "n4_you_to_omou",
        "name": "〜ようと思う",
        "level": "N4",
        "meaning": "打算……；想要……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "よう"},
            {"surface": "と"},
            {"lemma": "思う"}
        ]
    },
    {
        "id": "n4_tsumori",
        "name": "〜つもり",
        "level": "N4",
        "meaning": "打算……；准备……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "つもり"}
        ]
    },
    
    # ========================================================================
    # N3 句型 (中级句型)
    # ========================================================================
    
    {
        "id": "n3_tokini",
        "name": "〜とき（に）",
        "level": "N3",
        "meaning": "……的时候",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "とき"}
        ]
    },
    {
        "id": "n3_toshitemo",
        "name": "〜としても",
        "level": "N3",
        "meaning": "即使……；就算……",
        "pattern": [
            {"pos": "動詞"},
            {"surface": "と"},
            {"lemma": "する"},
            {"pos": "助詞"}
        ]
    },
    {
        "id": "n3_nimokakawarazu",
        "name": "〜にもかかわらず",
        "level": "N3",
        "meaning": "尽管……；虽然……",
        "pattern": [
            {"pos": "動詞"},
            {"surface": "に"},
            {"surface": "も"},
            {"lemma": "かかわる"},
            {"lemma": "ず"}
        ]
    },
    {
        "id": "n3_tameni",
        "name": "〜ために",
        "level": "N3",
        "meaning": "为了……；因为……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "ため"},
            {"surface": "に"}
        ]
    },
    {
        "id": "n3_yoni",
        "name": "〜ように",
        "level": "N3",
        "meaning": "为了……；以便……；使……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "よう"},
            {"surface": "に"}
        ]
    },
    {
        "id": "n3_yoni_naru",
        "name": "〜ようになる",
        "level": "N3",
        "meaning": "变得……；开始能够……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "よう"},
            {"surface": "に"},
            {"lemma": "なる"}
        ]
    },
    {
        "id": "n3_yoni_suru",
        "name": "〜ようにする",
        "level": "N3",
        "meaning": "努力做到……；尽量……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "よう"},
            {"surface": "に"},
            {"lemma": "する"}
        ]
    },
    {
        "id": "n3_bakari",
        "name": "〜ばかり",
        "level": "N3",
        "meaning": "刚刚……；光是……；总是……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "ばかり"}
        ]
    },
    {
        "id": "n3_mono",
        "name": "〜もの",
        "level": "N3",
        "meaning": "因为……（说明理由）",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "もの"}
        ]
    },
    {
        "id": "n3_wake",
        "name": "〜わけ",
        "level": "N3",
        "meaning": "……的理由；当然……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "わけ"}
        ]
    },
    {
        "id": "n3_wake_ga_nai",
        "name": "〜わけがない",
        "level": "N3",
        "meaning": "不可能……；不会……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "わけ"},
            {"surface": "が"},
            {"lemma": "ない"}
        ]
    },
    {
        "id": "n3_wake_niwa_ikanai",
        "name": "〜わけにはいかない",
        "level": "N3",
        "meaning": "不能……；没办法……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "わけ"},
            {"surface": "に"},
            {"surface": "は"},
            {"lemma": "行く"},
            {"lemma": "ない"}
        ]
    },
    {
        "id": "n3_dake",
        "name": "〜だけ",
        "level": "N3",
        "meaning": "只……；仅……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "だけ"}
        ]
    },
    {
        "id": "n3_shika_nai",
        "name": "〜しかない",
        "level": "N3",
        "meaning": "只有……；只能……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "しか"},
            {"lemma": "ない"}
        ]
    },
    {
        "id": "n3_te_shimau",
        "name": "〜てしまう",
        "level": "N3",
        "meaning": "完全……；不小心……",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"lemma": "しまう"}
        ]
    },
    {
        "id": "n3_te_oku",
        "name": "〜ておく",
        "level": "N3",
        "meaning": "事先……；提前……",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"lemma": "おく"}
        ]
    },
    {
        "id": "n3_te_miru",
        "name": "〜てみる",
        "level": "N3",
        "meaning": "试着……；做……看看",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"lemma": "みる"}
        ]
    },
    {
        "id": "n3_te_kuru",
        "name": "〜てくる",
        "level": "N3",
        "meaning": "……起来；越来越……",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"lemma": "くる"}
        ]
    },
    {
        "id": "n3_te_iku",
        "name": "〜ていく",
        "level": "N3",
        "meaning": "……下去；逐渐……",
        "pattern": [
            {"pos": "動詞"},
            {"pos": "助詞"},
            {"lemma": "いく"}
        ]
    },
    
    # 被动/使役
    {
        "id": "n3_rareru_passive",
        "name": "〜（ら）れる（被动）",
        "level": "N3",
        "meaning": "被……",
        "pattern": [
            {"pos": "動詞", "conj": "未然形"},
            {"lemma": "れる"}
        ]
    },
    {
        "id": "n3_saseru",
        "name": "〜（さ）せる",
        "level": "N3",
        "meaning": "让……；使……",
        "pattern": [
            {"pos": "動詞", "conj": "未然形"},
            {"lemma": "せる"}
        ]
    },
    
    # 比较/程度
    {
        "id": "n3_hodo",
        "name": "〜ほど",
        "level": "N3",
        "meaning": "……程度；越……越……",
        "pattern": [
            {"pos": "動詞"},
            {"lemma": "ほど"}
        ]
    },
    {
        "id": "n3_yori",
        "name": "〜より",
        "level": "N3",
        "meaning": "比……",
        "pattern": [
            {"pos": "名詞"},
            {"surface": "より"}
        ]
    },
]


def build_grammar_database():
    """构建句型规则数据库"""
    return GRAMMAR_RULES


def save_grammar_rules(rules, output_path):
    """保存句型规则到JSON文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {len(rules)} 条句型规则到 {output_path}")


if __name__ == "__main__":
    # 构建句型规则数据库
    rules = build_grammar_database()
    
    # 保存到 data 目录
    output_path = Path(__file__).parent.parent / "data" / "grammar_rules.json"
    save_grammar_rules(rules, output_path)
    
    # 打印统计信息
    n5_count = sum(1 for r in rules if r["level"] == "N5")
    n4_count = sum(1 for r in rules if r["level"] == "N4")
    n3_count = sum(1 for r in rules if r["level"] == "N3")
    n2_count = sum(1 for r in rules if r["level"] == "N2")
    n1_count = sum(1 for r in rules if r["level"] == "N1")
    
    print(f"\n📊 句型统计:")
    print(f"  N5: {n5_count} 条")
    print(f"  N4: {n4_count} 条")
    print(f"  N3: {n3_count} 条")
    print(f"  N2: {n2_count} 条")
    print(f"  N1: {n1_count} 条")
    print(f"  总计: {len(rules)} 条")
    
    print(f"\n📝 句型列表:")
    for rule in rules:
        print(f"  [{rule['level']}] {rule['name']} - {rule['meaning']}")
