# -*- coding: utf-8 -*-
"""启动 AnythingLLM Desktop（Electron）并通过 CDP 采集界面截图。

注意：本机环境变量 ELECTRON_RUN_AS_NODE=1 会让 Electron 以纯 Node 模式启动，
必须先取消该变量，否则所有命令行参数都会被当作 Node 参数而报 "bad option"。

用法：python shot_electron.py
截图输出到 screenshots/ 目录。"""
import asyncio, os, sys, io, subprocess, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.async_api import async_playwright

APP = r"project/学习//Ai前沿技术/项目4/anythingLLM/AnythingLLM.exe"
OUT = r"project/学习//Ai前沿技术/项目4/screenshots"
CDP = "http://127.0.0.1:9333"
os.makedirs(OUT, exist_ok=True)


async def shot(page, name, full=False):
    path = os.path.join(OUT, name)
    await page.screenshot(path=path, full_page=full)
    print("saved", name)


async def main():
    env = dict(os.environ)
    env.pop("ELECTRON_RUN_AS_NODE", None)
    proc = subprocess.Popen([APP, "--remote-debugging-port=9333"],
                            cwd=os.path.dirname(APP), env=env)
    try:
        await asyncio.sleep(30)
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(CDP)
            pages = browser.contexts[0].pages
            print("pages:", len(pages))
            page = pages[0]
            await page.wait_for_timeout(10000)
            print("TITLE:", await page.title())
            print("URL:", page.url)
            txt = await page.inner_text("body")
            print("BODY:", txt[:1000].replace("\n", " | "))
            await shot(page, "01_home.png")
            await browser.close()
    finally:
        proc.terminate()


asyncio.run(main())
