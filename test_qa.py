# -*- coding: utf-8 -*-
"""知识库问答测试：5个测试问题，逐条记录回答、引用来源与 token 指标。

每个问题使用独立的 thread（单轮对话），避免多轮历史干扰检索与生成，
对应参考文档中“New Thread 开启新对话”的操作。

用法：python test_qa.py
结果写入 qa_results.json，供说明引用。"""
import requests, json, sys, io, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"project/学习//Ai前沿技术/项目4")
from sse_client import collect, iter_events

B = "http://127.0.0.1:3001"
s = requests.Session(); s.trust_env = False
slug = s.get(B + "/api/workspaces", timeout=30).json()["workspaces"][0]["slug"]

# 工作区参数：仅基于上传文档回答（query 模式），提高召回条数
s.post(B + f"/api/workspace/{slug}/update",
       json={"chatMode": "query", "chatProvider": "ollama", "chatModel": "qwen3:8b",
             "openAiTemp": 0.1, "similarityThreshold": 0.25, "topN": 8},
       timeout=60)


def new_thread():
    r = s.post(B + f"/api/workspace/{slug}/thread/new", json={}, timeout=60)
    return r.json()["thread"]["slug"]


def ask(q, thread_slug):
    r = s.post(B + f"/api/workspace/{slug}/thread/{thread_slug}/stream-chat",
               json={"message": q, "mode": "query"},
               timeout=900, stream=True)
    r.encoding = "utf-8"
    buf = "".join(r.iter_content(chunk_size=None, decode_unicode=True))
    text, sources, metrics = collect([buf])
    if not sources:  # 从 chunk 里再取一次 sources
        for e in iter_events(buf):
            if e.get("type") == "textResponseChunk" and e.get("sources"):
                sources = e["sources"]
                break
    # 去掉 qwen3 的 <think> 段
    if "</think>" in text:
        text = text.split("</think>", 1)[1].strip()
    return text, sources, metrics


QS = [
    ("RAG的三个核心组件是什么？各自作用是什么？",
     "知识库"),
    ("AI Agent的“感知-决策-行动”闭环具体指什么？",
     "感知"),
    ("任务4的实践目的是什么？",
     "本地知识库搭建流程|掌握智能体的创建与应用"),
    ("AnythingLLM配置Embedder首选项要用哪个嵌入模型？它的作用是什么？",
     "nomic-embed-text"),
    ("豆包语音识别ASR的v3接口鉴权需要哪些请求头？audio.format必须填什么？",
     "pcm"),
]

results = []
for q, expect in QS:
    t0 = time.time()
    th = new_thread()
    print("=" * 72)
    print("【问题】", q)
    txt, src, metrics = ask(q, th)
    print("【回答】", txt[:1500])
    if src:
        print("【引用来源】")
        for x in src[:5]:
            print("   -", x.get("title"), "| score", round(x.get("score", 0), 3))
    if metrics:
        print("【指标】模型=%s provider=%s 输出tokens=%s 输入tokens=%s 用时=%.1fs"
              % (metrics.get("model"), metrics.get("provider"),
                 metrics.get("completion_tokens"), metrics.get("prompt_tokens"),
                 time.time() - t0))
    # 关键词判定：忽略空白差异；expect 多个关键词用 | 分隔，任一命中即算命中
    norm = lambda x: re.sub(r'\s+', '', x.lower())
    nt = norm(txt)
    hit = any(norm(k) in nt for k in expect.split('|'))
    print("【关键词命中】", expect, "=>", hit)
    results.append({
        "question": q, "answer": txt, "expect": expect, "hit": hit,
        "thread": th,
        "sources": [{"title": x.get("title"), "score": x.get("score"),
                     "url": x.get("url")} for x in src],
        "metrics": metrics,
    })
    print()

out = r"project/学习//Ai前沿技术/项目4/qa_results.json"
json.dump(results, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("命中", sum(1 for r in results if r["hit"]), "/", len(results))
print("结果已写入", out)
