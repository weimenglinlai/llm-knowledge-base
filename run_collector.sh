#!/bin/bash
# 启动 AnythingLLM 文档处理 collector
export NODE_ENV=production
export STORAGE_DIR="E://网页//学习////Ai前沿技术//项目4//storage"
export COLLECTOR_PORT=8888
export DATABASE_URL="file:$STORAGE_DIR/anythingllm.db"
cd "$(dirname "$0")/anythingLLM/resources/backend"
exec node collector.js
