# 配置 AnythingLLM：Ollama(qwen3:8b) + nomic-embed-text + LanceDB
import requests, json
B="http://127.0.0.1:3001"
s=requests.Session(); s.trust_env=False

def update(payload, label):
    r=s.post(B+"/api/system/update-env", json=payload, timeout=60)
    d=r.json()
    ok = not d.get("error")
    print(f"[{'OK ' if ok else 'ERR'}] {label}: {json.dumps(d, ensure_ascii=False)[:220]}")
    return ok

cfg = {
  "LLM_PROVIDER": "ollama",
  "LLM_MODEL": "qwen3:8b",
  "OllamaLLMBasePath": "http://127.0.0.1:11434",
  "OllamaLLMModelPref": "qwen3:8b",
  "OllamaLLMTokenLimit": 8192,
  "OllamaLLMKeepAliveSeconds": 300,
  "EmbeddingEngine": "ollama",
  "EmbeddingModelPref": "nomic-embed-text",
  "EmbeddingBasePath": "http://127.0.0.1:11434",
  "VectorDB": "lancedb",
  "DISABLE_FETCH_EMBEDDINGS": "false",
}
update(cfg, "full config")
