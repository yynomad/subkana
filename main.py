from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import sudachipy
from sudachipy import tokenizer

app = FastAPI(title="Japanese Tokenizer API")

# 初始化 Sudachi 分词器（使用 A 模式：最细粒度）
tokenizer_obj = tokenizer.Tokenizer()
mode = tokenizer.Tokenizer.SplitMode.C  # C 模式：平衡（推荐）

class SentenceRequest(BaseModel):
    text: str

@app.post("/tokenize")
def tokenize(request: SentenceRequest) -> List[str]:
    tokens = tokenizer_obj.tokenize(request.text, mode)
    words = [token.surface() for token in tokens]
    return words

@app.get("/health")
def health():
    return {"status": "ok"}