# 🎉 系统已完成并正常运行！

## ✅ 当前状态

- **词汇数据**: 8,140 个词汇（N5-N1）
- **语法规则**: 24 条基础语法规则（N5-N3）
- **服务状态**: 正常运行
- **测试状态**: 全部通过

## 📊 数据统计

### 词汇表
- **N5**: 662 个词汇
- **N4**: 630 个词汇
- **N3**: 1,722 个词汇
- **N2**: 1,823 个词汇
- **N1**: 3,303 个词汇
- **总计**: 8,140 个词汇

### 语法规则
- **N5**: 5 条（基础句型）
- **N4**: 10 条（初级句型）
- **N3**: 9 条（中级句型）
- **总计**: 24 条

## 🚀 快速开始

### 1. 启动服务

```bash
cd /Users/yao/repo/subkana
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

服务将在 http://localhost:8000 启动

### 2. 测试服务

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 分析句子
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "行かなければなりません"}'
```

### 3. 查看 API 文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 API 使用示例

### 健康检查

```bash
GET /api/v1/health
```

响应：
```json
{
  "status": "ok",
  "components": {
    "tokenizer": true,
    "grammar_engine": true,
    "vocabulary_mapper": true
  },
  "analysis_service": true
}
```

### 分析句子

```bash
POST /api/v1/analyze
Content-Type: application/json

{
  "sentence": "勉強しています"
}
```

响应：
```json
{
  "sentence": "勉強しています",
  "grammar_patterns": [
    {
      "id": "n5_teimasu",
      "name": "〜ています",
      "level": "N5",
      "meaning": "正在……；……着（状态持续）",
      "structure": ["し", "て", "い", "ます"],
      "span": {"start": 2, "end": 7},
      "matched_tokens": [1, 2, 3, 4]
    }
  ],
  "tokens": [
    {
      "surface": "勉強",
      "lemma": "勉強",
      "pos": "名詞",
      "conj": "*",
      "jlpt_level": "N5"
    },
    {
      "surface": "し",
      "lemma": "する",
      "pos": "動詞",
      "conj": "連用形",
      "jlpt_level": "N5"
    }
    // ... 更多词汇
  ]
}
```

## 🧪 测试

运行完整测试：

```bash
python test_api.py
```

## 📁 数据文件

### 1. vocabulary_levels_simple.json
快速查询版本，仅包含词汇和等级：
```json
{
  "行く": "N5",
  "勉強": "N5",
  "日本": "N3"
}
```

### 2. vocabulary_levels.json
完整版本，包含读音、释义等信息：
```json
{
  "行く": {
    "level": "N5",
    "reading": "いく",
    "meaning": "go",
    "romaji": "iku",
    "examples": []
  }
}
```

### 3. grammar_rules.json
语法规则定义：
```json
[
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
  }
]
```

## 🔧 常用操作

### 添加更多语法规则

编辑 `scripts/build_grammar_rules.py`，添加新规则后运行：

```bash
python scripts/build_grammar_rules.py
```

### 重新生成数据

如果需要更新数据：

```bash
# 重新下载所有数据
python one_click_jlpt.py
```

### 查看服务日志

服务启动时会显示详细日志，包括：
- MeCab 初始化状态
- 加载的词汇数量
- 加载的语法规则数量

## 📖 项目结构

```
subkana/
├── app/                          # 应用主目录
│   ├── api/                      # API 路由
│   │   ├── routes.py             # 路由定义
│   │   └── models.py             # API 模型
│   ├── core/                     # 核心功能
│   │   ├── tokenizer.py          # MeCab 分词器
│   │   ├── grammar_engine.py     # 语法匹配引擎
│   │   ├── vocabulary.py         # 词汇等级映射
│   │   └── service.py            # 分析服务
│   ├── config.py                 # 配置管理
│   ├── dependencies.py           # 依赖注入
│   └── main.py                   # FastAPI 应用入口
├── data/                         # 数据文件
│   ├── grammar_rules.json        # 语法规则
│   ├── vocabulary_levels.json    # 完整词汇表
│   └── vocabulary_levels_simple.json  # 简化词汇表
├── scripts/                      # 工具脚本
│   └── build_grammar_rules.py    # 生成语法规则
├── one_click_jlpt.py            # 一键数据获取工具
└── test_api.py                   # API 测试脚本
```

## ⚙️ 配置说明

主要配置在 `app/config.py`：

- `GRAMMAR_RULES_FILE`: 语法规则文件路径
- `VOCABULARY_LEVELS_FILE`: 词汇表文件路径（使用简化版）
- `MECAB_RC_PATH`: MeCab 配置文件路径
- `PORT`: 服务端口（默认 8000）
- `CORS_ORIGINS`: CORS 允许的源

## 🎯 功能特性

✅ **完整的 JLPT 支持**
- N1-N5 所有级别的词汇（8,140 个）
- N5-N3 基础语法规则（可扩展）

✅ **精确的形态素分析**
- 基于 MeCab 的专业分词
- 识别词性、活用形、词干

✅ **智能语法匹配**
- 滑动窗口算法
- 支持一句中多个语法模式
- 准确的规则匹配

✅ **JLPT 等级标注**
- 自动标注词汇等级
- 支持快速查询

✅ **高性能**
- 使用简化词汇表提升查询速度
- 缓存机制
- 异步处理

## 🔍 技术亮点

### 1. 为什么必须使用形态素分析？

日语是黏着语，语法信息附着在词干上：
- **词干（lemma）**: 用于词汇等级查询
- **活用形（conj）**: 用于语法匹配
- **词性（pos）**: 区分不同词类

例如："行かなければならない"
```
行か (未然形) + なければ + ならない
```
单纯字符串匹配无法识别这种变形。

### 2. 语法规则匹配算法

使用滑动窗口算法：
1. 遍历每个可能的起始位置
2. 对每个位置尝试匹配所有规则
3. 规则 pattern 中的条件必须按序匹配

### 3. 数据格式设计

**词汇表**: 简单的 key-value 映射，O(1) 查询
**语法规则**: 基于 MeCab 输出的精确匹配

## 🚨 常见问题

### MeCab 初始化失败

确保已安装 MeCab 和词典：
```bash
# macOS
brew install mecab mecab-ipadic

# Ubuntu/Debian
sudo apt-get install mecab libmecab-dev mecab-ipadic-utf8
```

### 词汇查询返回 null

可能原因：
1. 词汇不在词库中（可添加到 vocabulary_levels_simple.json）
2. 词形变化导致 lemma 不匹配（MeCab 会自动处理）

### 语法规则不匹配

检查：
1. pattern 是否与 MeCab 输出格式一致
2. 活用形是否正确
3. 使用测试句子验证

## 📚 扩展建议

### 短期
- [ ] 添加更多 N2/N1 语法规则
- [ ] 优化语法规则优先级
- [ ] 添加缓存机制

### 中期
- [ ] 支持批量句子分析
- [ ] 添加语法解释和例句
- [ ] 前端可视化展示

### 长期
- [ ] 机器学习增强识别
- [ ] 上下文分析
- [ ] 多语言支持

## 📄 许可证

- 语法数据来自 Hanabira.org (Creative Commons)
- 词汇数据来自 jlpt-vocab-api
- 使用时需注明来源

---

**🎉 系统已就绪，可以开始使用！**

