#!/bin/bash
# 项目4 一键启动：Ollama -> AnythingLLM 后端 -> collector -> 前端代理
cd "$(dirname "$0")"
BASE="$(pwd -W 2>/dev/null || pwd)"
mkdir -p logs

wait_port() {
  local port=$1 tries=${2:-40}
  for i in $(seq 1 $tries); do
    if curl -s --noproxy '*' -o /dev/null --max-time 3 "http://127.0.0.1:$port/api/ping" 2>/dev/null; then
      return 0
    fi
    sleep 2
  done
  return 1
}

echo "[1/4] 启动 Ollama ..."
bash run_ollama.sh > logs/ollama.log 2>&1 &
wait_port 11434 30 && echo "      Ollama OK" || echo "      Ollama 启动中/失败(可稍后重试)"

echo "[2/4] 启动 AnythingLLM 后端 ..."
bash run_allm_server.sh > logs/backend.log 2>&1 &
wait_port 3001 40 && echo "      后端 OK" || echo "      后端启动中"

echo "[3/4] 启动 collector ..."
bash run_collector.sh > logs/collector.log 2>&1 &
wait_port 8888 30 && echo "      collector OK" || echo "      collector 启动中"

echo "[4/4] 启动前端代理 ..."
node serve_frontend.js > logs/frontend.log 2>&1 &
sleep 3
echo "      前端 http://127.0.0.1:8088"

echo
echo "全部服务已拉起。停止：taskkill 或结束对应 node/ollama 进程。"
