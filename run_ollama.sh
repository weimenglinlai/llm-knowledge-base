#!/bin/bash
# 启动本项目使用的 Ollama 服务（模型目录指向系统 OLLAMA_MODELS）
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_KEEP_ALIVE=300
OLLAMA_BIN="~/AppData/Local/Programs/Ollama/ollama.exe"
exec "$OLLAMA_BIN" serve
