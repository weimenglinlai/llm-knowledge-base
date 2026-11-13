#!/bin/bash
# 启动 AnythingLLM 后端服务（数据目录位于项目4下）
export DISABLE_SWAGGER_DOCS=true
export NODE_ENV=production
export STORAGE_DIR="E://网页//学习////Ai前沿技术//项目4//storage"
export SERVER_PORT=3001
export DATABASE_URL="file:$STORAGE_DIR/anythingllm.db"
export VECTOR_DB="lancedb"
export CACHE_DIR="$STORAGE_DIR/cache"
cd "$(dirname "$0")/anythingLLM/resources/backend"
exec node server.js
