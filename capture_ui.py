# -*- coding: utf-8 -*-
"""用原生 CDP（websocket）驱动 AnythingLLM Desktop，采集说明所需的界面截图。

Playwright 的 connect_over_cdp 与旧版 Electron（Chrome 126）握手不兼容，
因此这里直接用 websocket 走 Chrome DevTools Protocol。

前置：先启动桌面版（常驻）
    cd "project/学习//Ai前沿技术/项目4/anythingLLM"
    env -u ELECTRON_RUN_AS_NODE ./AnythingLLM.exe --remote-debugging-port=9333

注意：本机环境变量 ELECTRON_RUN_AS_NODE=1 会让 Electron 以纯 Node 模式启动，
必须先取消该变量，否则命令行参数会被当作 Node 参数而报 "bad option"。

用法：python capture_ui.py
截图输出到 screenshots/ 目录。"""
import asyncio, os, sys, io, json, base64, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import websockets

CDP_HOST = "http://127.0.0.1:9333"
OUT = r"project/学习//Ai前沿技术/项目4/screenshots"
os.makedirs(OUT, exist_ok=True)


def http_json(path):
    # 本机设了 HTTP_PROXY，urllib 会把 localhost 也交给代理，必须显式绕过
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(CDP_HOST + path, timeout=10) as r:
        return json.loads(r.read().decode())


class CDP:
    def __init__(self, ws):
        self.ws = ws
        self.id = 0

    async def call(self, method, params=None):
        self.id += 1
        mid = self.id
        await self.ws.send(json.dumps(
            {"id": mid, "method": method, "params": params or {}}))
        while True:
            raw = await asyncio.wait_for(self.ws.recv(), timeout=120)
            data = json.loads(raw)
            if data.get("id") == mid:
                if "error" in data:
                    raise RuntimeError(f"{method} -> {data['error']}")
                return data.get("result", {})

    async def eval(self, expr):
        r = await self.call("Runtime.evaluate",
                            {"expression": expr, "returnByValue": True,
                             "awaitPromise": True})
        res = r.get("result", {})
        if res.get("subtype") == "error":
            raise RuntimeError(res.get("description"))
        return res.get("value")


async def main():
    targets = http_json("/json/list")
    pages = [t for t in targets if t.get("type") == "page"
             and "devtools" not in t.get("url", "")]
    if not pages:
        print("no page target"); return

    async with websockets.connect(pages[0]["webSocketDebuggerUrl"],
                                  max_size=200 * 1024 * 1024) as ws:
        cdp = CDP(ws)
        await cdp.call("Page.enable")
        await cdp.call("Runtime.enable")
        await asyncio.sleep(2)

        async def snap(name, full=False):
            r = await cdp.call("Page.captureScreenshot",
                               {"format": "png", "captureBeyondViewport": full})
            data = base64.b64decode(r["data"])
            open(os.path.join(OUT, name), "wb").write(data)
            print("saved", name, len(data) // 1024, "KB")

        async def goto(hash_path, wait=6000):
            await cdp.eval(f"location.hash = '{hash_path}'")
            await asyncio.sleep(wait / 1000)
            url = await cdp.eval("location.href")
            body = await cdp.eval("document.body.innerText.slice(0,400)")
            print(f"  -> {hash_path} | {url.split('#')[-1]}")
            print("     ", (body or "").replace("\n", " | ")[:220])

        async def text(sel):
            return await cdp.eval(
                f"(document.querySelector({json.dumps(sel)})||{{}}).innerText || ''")

        # 1. 工作区列表（首页）
        await goto("#/", 7000)
        await snap("01_workspace_list.png")

        # 2. 设置 - LLM 提供商（Ollama + 模型）
        await goto("#/settings/llm-preference", 7000)
        await snap("02_settings_llm.png")

        # 3. 设置 - 嵌入器（Embedder = nomic-embed-text）
        await goto("#/settings/embedding-preference", 7000)
        await snap("03_settings_embedder.png")

        # 4. 设置 - 向量数据库
        await goto("#/settings/vector-database", 7000)
        await snap("04_settings_vector_db.png")

        # 5. 工作区 - 文档列表（上传记录）
        ws_slug = "25db1e64-3bff-4d00-81c1-29188b6dc03b"
        await goto(f"#/workspace/{ws_slug}", 9000)
        await snap("05_workspace_chat.png")

        print("done")


asyncio.run(main())
