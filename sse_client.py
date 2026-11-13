# -*- coding: utf-8 -*-
"""解析 AnythingLLM stream-chat 的 SSE 流。

后端实际推送的事件类型：
  textResponseChunk       —— 增量文本（textResponse 字段，分片推送）
  textResponseContext     —— 检索到的上下文片段
  finalizeResponseStream  —— 结束帧，含 metrics（token 数、模型、provider、耗时）

注意：帧分隔不是标准的 \\n\\n，而是连续拼接的 `data: {...}`，
因此用 JSONDecoder.raw_decode 做深度扫描逐个提取对象。
"""
import json

_TEXT_TYPES = ("textResponse", "textResponseChunk")
_FINAL_TYPES = ("finalizeResponseStream", "finalResponse")


def iter_events(text):
    dec = json.JSONDecoder()
    i, n = 0, len(text)
    while i < n:
        j = text.find('{"', i)
        if j < 0:
            break
        try:
            obj, end = dec.raw_decode(text, j)
        except ValueError:
            i = j + 1
            continue
        if isinstance(obj, dict) and "type" in obj:
            yield obj
        i = end


def collect(chunks):
    """把流式响应聚合成 (text, sources, metrics)"""
    buf = "".join(chunks)
    text = ""
    sources = []
    metrics = None
    for d in iter_events(buf):
        t = d.get("type")
        if t in _TEXT_TYPES:
            piece = d.get("textResponse")
            if piece:
                text += piece
        elif t == "textResponseContext":
            for x in (d.get("sources") or d.get("results") or []):
                if isinstance(x, dict):
                    sources.append(x)
        elif t in _FINAL_TYPES:
            if d.get("sources"):
                sources = d["sources"]
            if d.get("metrics"):
                metrics = d["metrics"]
            if d.get("textResponse"):
                text = d["textResponse"]
    return text.strip(), sources, metrics
