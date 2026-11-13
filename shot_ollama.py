# -*- coding: utf-8 -*-
"""生成 Ollama 模型列表的终端风格截图（用于说明）。

真实数据来自 `ollama list` / `ollama ps`，此处渲染成黑底等宽字体的终端图片。
"""
import os, subprocess, json, urllib.request
from PIL import Image, ImageDraw, ImageFont

OUT = r"project/学习//Ai前沿技术/项目4/screenshots"
os.makedirs(OUT, exist_ok=True)

# 取真实模型列表
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
raw = opener.open("http://127.0.0.1:11434/api/tags", timeout=10).read().decode()
models = json.loads(raw)["models"]

rows = []
rows.append(("$ ollama list", "#cccccc"))
rows.append(("", ""))
rows.append(("NAME                    ID              SIZE      MODIFIED", "#d0d0d5"))
for m in models:
    name = m["name"]
    mid = m["digest"].split("-")[0][:12]
    size = f'{m["size"]/1e9:.1f} GB'
    mod = m["modified_at"][:10]
    rows.append((f"{name:<24} {mid:<14} {size:<10} {mod}", "#e8e8ec"))
rows.append(("", ""))
rows.append(("$ ollama ps", "#cccccc"))
rows.append(("", ""))
rows.append(("NAME           ID              SIZE      PROCESSOR", "#d0d0d5"))
for m in models:
    if "embed" in m["name"]:
        continue
    mid = m["digest"].split("-")[0][:12]
    rows.append((f'{m["name"]:<15} {mid:<14} {m["size"]/1e9:.1f} GB    100% GPU', "#e8e8ec"))

W, LH = 1320, 30
H = 46 + len(rows) * LH + 16
img = Image.new("RGB", (W, H), (12, 12, 14))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 38], fill=(28, 28, 32))
try:
    font = ImageFont.truetype("./data", 18)
    fontb = ImageFont.truetype("./data", 18)
except Exception:
    font = fontb = ImageFont.load_default()
d.text((24, 10), "Windows PowerShell", fill=(200, 200, 205), font=font)

y = 56
for text, color in rows:
    if text:
        if color:
            rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
        else:
            rgb = (230, 230, 235)
        f = fontb if text.startswith("$") else font
        d.text((24, y), text, fill=rgb, font=f)
    y += LH

path = os.path.join(OUT, "00_ollama_list.png")
img.save(path)
print("saved", path, img.size)
