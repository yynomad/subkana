# 日语句子分析后端 API

基于 MeCab 的日语句子分析服务，提供句型结构和单词等级分析。

## 项目特性

- ✅ 基于 MeCab 的形态素分析
- ✅ 规则驱动的句型匹配引擎
- ✅ JLPT 词汇等级映射
- ✅ 完整的配置管理系统（环境变量）
- ✅ 结构化日志
- ✅ CORS 支持（Chrome 扩展友好）
- ✅ 依赖注入和服务管理
- ✅ 类型提示和 Pydantic 模型验证

## 前置要求

### 1. 安装 MeCab 和 IPADIC 词典

**macOS (使用 Homebrew):**
```bash
brew install mecab
brew install mecab-ipadic
```

**Ubuntu/Debian:**
```bash
sudo apt-get install mecab libmecab-dev mecab-ipadic-utf8
```

**验证安装:**
```bash
mecab --version
echo "テスト" | mecab
```

### 2. Python 环境

确保已安装 Python 3.8+

## 快速开始

### 1. 克隆项目并进入目录

```bash
cd subkana
```

### 2. 创建虚拟环境（如果还没有）

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量（可选）

复制 `.env.example` 为 `.env` 并根据需要修改：

```bash
cp .env.example .env
```

主要配置项：
- `PORT`: 服务器端口（默认 8000）
- `DEBUG`: 调试模式（默认 false）
- `CORS_ORIGINS`: CORS 允许的源（开发环境可使用 `["*"]`）

### 5. 启动服务器

**方式 1：使用 uvicorn 直接启动**
```bash
uvicorn app.main:app --reload
```

**方式 2：使用 Python 启动脚本**
```bash
python main.py
```

服务器将在 `http://localhost:8000` 启动。

### 6. 访问 API 文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 使用示例

### 健康检查

```bash
curl http://localhost:8000/api/v1/health
```

### 分析句子

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "行かなければなりません"}'
```

### 测试用例

```bash
# 测试用例 1
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "行かなければなりません"}'

# 测试用例 2
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "勉強しなければならない"}'
```

## 项目结构

```
subkana/
├── app/                      # 应用主目录
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py             # 配置管理
│   ├── dependencies.py      # 依赖注入
│   ├── exceptions.py         # 自定义异常
│   ├── middleware.py        # 中间件
│   ├── logging_config.py     # 日志配置
│   ├── api/                  # API 路由
│   │   ├── __init__.py
│   │   ├── routes.py         # 路由定义
│   │   └── models.py         # API 模型
│   └── core/                 # 核心功能
│       ├── __init__.py
│       ├── models.py         # 数据模型
│       ├── tokenizer.py       # MeCab 封装
│       ├── grammar_engine.py  # 句型规则匹配引擎
│       ├── vocabulary.py      # 词汇等级映射
│       └── service.py         # 分析服务
├── data/                     # 数据文件
│   ├── grammar_rules.json    # 句型规则定义
│   └── vocabulary_levels.json # 词汇等级映射表
├── main.py                   # 启动脚本
├── requirements.txt          # Python 依赖
├── .env.example              # 环境变量示例
└── README.md                 # 项目文档
```

## 配置说明

### 环境变量

所有配置通过环境变量管理，支持 `.env` 文件。主要配置项：

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `PORT` | int | 8000 | 服务器端口 |
| `HOST` | str | 0.0.0.0 | 服务器主机 |
| `DEBUG` | bool | false | 调试模式 |
| `ENVIRONMENT` | str | development | 环境类型 |
| `CORS_ORIGINS` | List[str] | ["*"] | CORS 允许的源 |
| `LOG_LEVEL` | str | INFO | 日志级别 |
| `GRAMMAR_RULES_FILE` | str | data/grammar_rules.json | 句型规则文件路径 |
| `VOCABULARY_LEVELS_FILE` | str | data/vocabulary_levels.json | 词汇等级文件路径 |

### CORS 配置

开发环境可以使用 `CORS_ORIGINS=["*"]` 允许所有源。

生产环境建议限制为特定域名：

```env
CORS_ORIGINS=["https://www.youtube.com","https://www.netflix.com"]
```

## 开发说明

### 添加新句型

在 `data/grammar_rules.json` 中添加新规则：

```json
{
  "id": "n3_example",
  "name": "〜例",
  "level": "N3",
  "meaning": "例如……",
  "pattern": [
    {"pos": "名詞"},
    {"surface": "例"}
  ]
}
```

### 添加词汇等级

在 `data/vocabulary_levels.json` 中添加映射：

```json
{
  "新しい": "N5",
  "難しい": "N4"
}
```

### 修改端口

方式 1：环境变量
```bash
export PORT=8080
uvicorn app.main:app --reload
```

方式 2：直接指定
```bash
uvicorn app.main:app --reload --port 8080
```

## 架构设计

### 为什么句型识别必须基于形态素分析？

1. 日语是黏着语，语法信息（活用形、助词、助动词）都附着在词干上
2. 只有通过形态素分析才能准确提取：
   - 词干（lemma）：用于词汇等级查询
   - 活用形（conj）：用于句型匹配（如"未然形"+"なければ"）
   - 词性（pos）：区分动词、助动词、助词等
3. 单纯字符串匹配无法处理同形异义（如"行く"的未然形"行か" vs "行く"的连用形"行き"）

### 为什么对前端只暴露一个 `/analyze` 接口？

1. 简化前端调用：一次请求获取所有信息（句型+词汇等级）
2. 减少网络往返：避免多次请求（tokenize + grammar + vocabulary）
3. 保证数据一致性：所有分析基于同一份形态素分析结果
4. 便于后续扩展：可以在后端统一处理缓存、优化等逻辑

## 后续扩展方向

1. 增加 N3/N2/N1 句型：在 `data/grammar_rules.json` 中添加新规则即可
2. 支持前端 hover 高亮：span 字段已提供字符位置，前端可直接使用
3. 多句型冲突处理：当前返回所有匹配，可添加优先级或去重逻辑
4. 缓存机制：对相同句子进行缓存，提高性能
5. 批量分析：支持一次请求分析多个句子

## 部署

### Docker

```bash
docker build -t subkana .
docker run -p 8000:8000 subkana
```

### Railway / Render

项目已包含 `railway.toml` 和 `render.yml` 配置文件，可直接部署。

## 许可证

MIT
