# 日语字幕学习分析后端 API

基于大模型的日语字幕学习分析服务，提供自然翻译、句式拆分和重点单词/JLPT 等级说明。

## 项目特性

- ✅ 完全依靠大模型生成学习分析，不再依赖后台语法规则库或单词库
- ✅ 面向日语学习：自然翻译、句式分析、重点单词和语气说明
- ✅ 支持中文（zh）和英文（en）学习者解释语言
- ✅ 保留旧版 `grammar_patterns` / `tokens` 字段，方便已有前端逐步迁移
- ✅ 完整的配置管理系统（环境变量）
- ✅ 结构化日志
- ✅ CORS 支持（Chrome 扩展友好）
- ✅ 依赖注入和服务管理
- ✅ 类型提示和 Pydantic 模型验证

## 前置要求

### 1. 大模型 API

服务通过 OpenAI 兼容的 Chat Completions 接口调用大模型。至少需要配置：

```bash
export LLM_API_KEY=your_api_key
```

可选配置：

```bash
export LLM_BASE_URL=https://api.openai.com/v1
export LLM_MODEL=gpt-4o-mini
export LLM_TIMEOUT=60
export LLM_TEMPERATURE=0.2
```

也可以使用任何兼容 `/chat/completions` 的服务商，只要调整 `LLM_BASE_URL` 和 `LLM_MODEL`。

### 2. Python 环境

确保已安装 Python 3.10+

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
- `LLM_API_KEY`: 大模型 API Key（必填）
- `LLM_BASE_URL`: OpenAI 兼容接口地址（默认 `https://api.openai.com/v1`）
- `LLM_MODEL`: 大模型名称（默认 `gpt-4o-mini`）
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
  -d '{"sentence": "なめてしまいました", "target_language": "zh"}'
```

### 测试用例

```bash
# 测试用例 1
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "なめてしまいました", "target_language": "zh"}'

# 测试用例 2
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "相手をなめてしまいました", "target_language": "en"}'
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
│       ├── models.py         # 学习分析数据模型
│       ├── llm_client.py      # 大模型分析客户端
│       └── service.py         # 分析服务
├── data/                     # 旧版本地规则/词库数据（历史兼容）
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
| `LLM_API_KEY` | str | None | 大模型 API Key |
| `LLM_BASE_URL` | str | https://api.openai.com/v1 | OpenAI 兼容接口地址 |
| `LLM_MODEL` | str | gpt-4o-mini | 大模型名称 |
| `LLM_TIMEOUT` | int | 60 | 大模型请求超时秒数 |
| `LLM_TEMPERATURE` | float | 0.2 | 大模型输出随机性 |

### CORS 配置

开发环境可以使用 `CORS_ORIGINS=["*"]` 允许所有源。

生产环境建议限制为特定域名：

```env
CORS_ORIGINS=["https://www.youtube.com","https://www.netflix.com"]
```

## 开发说明

### 调整大模型分析提示词

核心提示词位于 `app/core/llm_client.py`。如果需要改变学习分析的深度、输出字段或语气，可优先调整 `_build_messages` 和 `_build_user_prompt`。

### 响应结构说明

新前端建议优先使用 `analysis` 字段：

- `analysis.translation`: 自然翻译
- `analysis.sentence_patterns`: 句式/语法拆分，例如 `なめる + てしまう + ました`
- `analysis.vocabulary`: 重点单词、读音、JLPT 等级、语气说明
- `analysis.notes`: 其他学习提示

`grammar_patterns` 和 `tokens` 是旧版兼容字段，后续可以逐步下线。

