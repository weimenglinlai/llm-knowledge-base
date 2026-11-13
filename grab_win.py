# -*- coding: utf-8 -*-
"""把指定窗口带到前台并按其客户区截图，保存到 screenshots/。

浏览器扩展模式下无法直接落盘截图，因此用 Win32 把目标窗口顶到最前，
再用 PIL 抓取该窗口客户区。

用法：python grab_win.py <输出文件名> <窗口标题关键字>
"""
import sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import win32gui, win32con, win32api
from PIL import ImageGrab

OUT = r"project/学习//Ai前沿技术/项目4/screenshots"
os.makedirs(OUT, exist_ok=True)


def find_window(keyword):
    hits = []

    def cb(h, _):
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h)
            if keyword in t:
                hits.append((h, t))
        return True

    win32gui.EnumWindows(cb, None)
    return hits


def bring_to_front(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    # AttachThreadInput 技巧：强制抢到前台
    fg = win32gui.GetForegroundWindow()
    tid_fg = win32process.GetWindowThreadProcessId(fg)[0]
    tid_tg = win32process.GetWindowThreadProcessId(hwnd)[0]
    try:
        win32process.AttachThreadInput(tid_fg, tid_tg, True)
    except Exception:
        pass
    win32gui.SetForegroundWindow(hwnd)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
    time.sleep(0.4)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    time.sleep(0.8)


import win32process  # noqa: E402  (放在 bring_to_front 之前导入)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "screen.png"
    keyword = sys.argv[2] if len(sys.argv) > 2 else "扣子"
    hits = find_window(keyword)
    if not hits:
        print("未找到窗口:", keyword)
        return
    # 优先取标题里包含关键词且不是 WorkBuddy 内嵌窗口的
    hwnd, title = hits[0]
    for h, t in hits:
        if "WorkBuddy" not in t and "Microsoft Edge" in t:
            hwnd, title = h, t
            break
    print("窗口:", title[:70])
    bring_to_front(hwnd)

    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    w, h = right - left, bottom - top
    sx, sy = win32gui.ClientToScreen(hwnd, (left, top))
    print("客户区:", w, h, "at", sx, sy)

    img = ImageGrab.grab(bbox=(sx, sy, sx + w, sy + h), all_screens=True)
    path = os.path.join(OUT, name)
    img.save(path)
    print("saved", path, img.size)


if __name__ == "__main__":
    main()
