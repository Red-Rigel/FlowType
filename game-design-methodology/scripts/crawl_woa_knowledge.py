#!/usr/bin/env python3
"""
爬取 game.woa.com 知识库 — 遇到 iOA 自动暂停，等待手动登录后继续。

用法:
  python3 crawl_woa_knowledge.py
  python3 crawl_woa_knowledge.py --start-url https://game.woa.com/knowledge/1013

登录流程:
  1. 脚本会打开可见浏览器窗口
  2. 若检测到 iOA/扫码/访问失败页面，自动暂停
  3. 请在浏览器中完成 iOA 登录
  4. 回到终端按 Enter 继续（脚本会再次校验是否已登录）

输出: ../raw-articles-woa/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Page, sync_playwright

DEFAULT_START = "https://game.woa.com/knowledge/1013"
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT = BASE_DIR / "raw-articles-woa"
PROFILE_DIR = BASE_DIR / ".browser-profile-woa"
STATE_FILE = OUTPUT / "crawl_state.json"
SCREENSHOT_DIR = OUTPUT / "screenshots"

IOA_MARKERS = (
    "iOA",
    "ioa.tencent.com",
    "访问失败",
    "请尝试以下方法",
    "扫码",
    "您正在尝试访问",
    "移动站点",
    "8000助手",
    "下载 ",
)

LOGIN_URL_MARKERS = (
    "qrcode_app",
    "no_qrcode_app",
)


def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def page_needs_ioa_login(page: Page) -> bool:
    """检测当前页面是否仍处于 iOA / 扫码 / 访问失败状态。"""
    try:
        url = page.url.lower()
        if "ioa.tencent.com" in url:
            return True
        html = page.content()
        text = page.inner_text("body")[:8000]
        combined = html + text
        if any(m in combined for m in LOGIN_URL_MARKERS):
            # 内网 gate 页面特征
            if "qrcode" in html.lower() or "访问失败" in text:
                return True
        if any(m in text for m in IOA_MARKERS):
            # 排除已正常进入知识库后的误报
            if "/knowledge/" in url and "访问失败" not in text:
                return False
            if "访问失败" in text or "iOA" in text:
                return True
        return False
    except Exception:
        return True


def wait_for_ioa_login(page: Page, context: str = "", poll_interval: float = 3.0) -> None:
    """遇到 iOA 时暂停：自动轮询检测登录完成，无需按 Enter。"""
    label = f"（{context}）" if context else ""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    shot = SCREENSHOT_DIR / f"ioa_wait_{datetime.now().strftime('%H%M%S')}.png"
    try:
        page.screenshot(path=str(shot), full_page=True)
        log(f"已保存当前页面截图: {shot}")
    except Exception:
        pass

    log("=" * 60)
    log(f"⏸  检测到 iOA / 登录拦截 {label}")
    log("请在浏览器窗口中完成 iOA 登录（扫码或账号登录）")
    log("登录成功后脚本将自动检测并继续，无需按 Enter")
    log("（若终端可交互，也可按 Enter 立即校验，输入 q 退出）")
    log("=" * 60)

    waited = 0
    while True:
        if not page_needs_ioa_login(page):
            log("✓ 登录校验通过，继续爬取...")
            return

        # 非阻塞：有输入则立即校验
        try:
            import select
            if select.select([sys.stdin], [], [], 0)[0]:
                choice = sys.stdin.readline().strip().lower()
                if choice == "q":
                    sys.exit(0)
                try:
                    page.reload(wait_until="domcontentloaded", timeout=60000)
                    time.sleep(1)
                except Exception:
                    pass
                if not page_needs_ioa_login(page):
                    log("✓ 登录校验通过，继续爬取...")
                    return
                log("仍未通过登录校验，请继续在浏览器中操作...")
        except Exception:
            pass

        waited += poll_interval
        if int(waited) % 15 == 0 and waited > 0:
            log(f"  … 等待登录中（已等待 {int(waited)}s），请在浏览器完成 iOA 登录")
            try:
                page.screenshot(path=str(shot), full_page=True)
            except Exception:
                pass

        time.sleep(poll_interval)
        try:
            # 用户可能在同页完成登录，轻量刷新检测
            page.reload(wait_until="domcontentloaded", timeout=60000)
            time.sleep(0.5)
        except Exception:
            pass


def ensure_logged_in(page: Page, url: str) -> None:
    log(f"打开页面: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=120000)
    time.sleep(2)
    if page_needs_ioa_login(page):
        wait_for_ioa_login(page, "首次访问")


def scroll_and_load_more(page: Page, max_rounds: int = 80) -> None:
    """滚动并点击翻页/加载更多。"""
    last_count = 0
    stale = 0
    for i in range(max_rounds):
        if page_needs_ioa_login(page):
            wait_for_ioa_login(page, "列表翻页中")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.0)
        clicked = False
        for sel in [
            "text=下一页",
            "text=加载更多",
            "text=查看更多",
            "button:has-text('更多')",
            ".pagination-next:not(.disabled)",
            "[aria-label='Next']",
            ".el-pagination__next:not(.is-disabled)",
            ".ant-pagination-next:not(.ant-pagination-disabled)",
        ]:
            try:
                loc = page.locator(sel).first
                if loc.count() and loc.is_visible():
                    loc.click(timeout=3000)
                    time.sleep(1.5)
                    clicked = True
                    break
            except Exception:
                continue
        links = collect_article_links(page)
        if len(links) == last_count:
            stale += 1
        else:
            stale = 0
            last_count = len(links)
        body = ""
        try:
            body = page.inner_text("body")
        except Exception:
            pass
        if stale >= 3 or "已经到最底" in body or "没有更多" in body:
            break
        if not clicked and stale >= 2:
            break
    log(f"列表滚动完成，当前发现 {last_count} 个文章链接")


def collect_article_links(page: Page) -> set[str]:
    hrefs = page.eval_on_selector_all(
        "a[href]",
        """els => els.map(e => e.href).filter(h =>
            /\\/knowledge\\/\\d+/.test(h) ||
            /\\/article\\/\\d+/.test(h) ||
            /\\/post\\/\\d+/.test(h)
        )""",
    )
    out: set[str] = set()
    for h in hrefs:
        h = h.split("#")[0].split("?")[0]
        if re.search(r"/(knowledge|article|post)/\d+", h):
            out.add(h)
    return out


def extract_article(page: Page, url: str) -> dict:
    if page_needs_ioa_login(page):
        wait_for_ioa_login(page, "抓取文章前")
    page.goto(url, wait_until="domcontentloaded", timeout=90000)
    time.sleep(1.5)
    if page_needs_ioa_login(page):
        wait_for_ioa_login(page, f"文章页 {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        time.sleep(1.5)
    title = page.title().strip()
    if title.endswith("-") or not title:
        h1 = page.query_selector("h1")
        title = h1.inner_text().strip() if h1 else url
    content = ""
    for sel in ["article", ".article-content", ".rich-content", ".content-body", "main", "#app"]:
        el = page.query_selector(sel)
        if el:
            content = el.inner_text()
            if len(content) > 200:
                break
    if len(content) < 200:
        content = page.inner_text("body")
    content = re.sub(r"\n{3,}", "\n\n", content)
    return {"url": url, "title": title, "content": content, "words": len(content)}


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"done_urls": [], "manifest": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def save_article(art: dict) -> str:
    m = re.search(r"/(\d+)$", art["url"])
    fid = m.group(1) if m else str(abs(hash(art["url"])))
    out = OUTPUT / f"{fid}.md"
    out.write_text(
        f"# {art['title']}\n\n"
        f"> 来源: {art['url']}\n"
        f"> 爬取时间: {datetime.now().isoformat(timespec='seconds')}\n\n"
        f"---\n\n{art['content']}",
        encoding="utf-8",
    )
    return fid


def main() -> None:
    parser = argparse.ArgumentParser(description="爬取 game.woa.com 知识库（iOA 交互登录）")
    parser.add_argument("--start-url", default=DEFAULT_START)
    parser.add_argument("--headless", action="store_true", help="无头模式（不推荐，无法手动登录）")
    parser.add_argument("--no-resume", action="store_true", help="忽略已爬取记录，全部重抓")
    args = parser.parse_args()

    if args.headless:
        log("警告: 无头模式无法手动登录 iOA，建议使用默认有界面模式")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    state = {"done_urls": [], "manifest": []} if args.no_resume else load_state()
    done = set(state.get("done_urls", []))

    log("启动浏览器（有界面模式，默认）...")
    log(f"用户数据目录: {PROFILE_DIR}（登录状态会保留）")
    log(f"输出目录: {OUTPUT}")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=args.headless,
            viewport={"width": 1400, "height": 900},
            locale="zh-CN",
            args=["--start-maximized"] if not args.headless else [],
        )
        page = context.pages[0] if context.pages else context.new_page()

        ensure_logged_in(page, args.start_url)
        scroll_and_load_more(page)
        all_links = collect_article_links(page)
        log(f"共发现 {len(all_links)} 篇文章链接")

        pending = sorted(all_links - done)
        log(f"待爬取: {len(pending)} 篇（已跳过 {len(done)} 篇）")

        for idx, url in enumerate(pending, 1):
            try:
                if page_needs_ioa_login(page):
                    wait_for_ioa_login(page, f"第 {idx}/{len(pending)} 篇")
                art = extract_article(page, url)
                if art["words"] < 100:
                    log(f"SKIP 内容过短: {url}")
                    continue
                fid = save_article(art)
                entry = {"id": fid, "title": art["title"], "url": url, "words": art["words"]}
                state["manifest"] = [e for e in state.get("manifest", []) if e.get("url") != url]
                state["manifest"].append(entry)
                done.add(url)
                state["done_urls"] = list(done)
                save_state(state)
                log(f"[{idx}/{len(pending)}] OK ({art['words']}字): {art['title'][:50]}")
                time.sleep(0.8)
            except KeyboardInterrupt:
                log("中断，进度已保存")
                save_state(state)
                context.close()
                sys.exit(0)
            except Exception as e:
                log(f"ERR {url}: {e}")

        manifest_path = OUTPUT / "manifest.json"
        manifest_path.write_text(
            json.dumps(state.get("manifest", []), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        context.close()

    log(f"全部完成，共 {len(state.get('manifest', []))} 篇 → {OUTPUT}")


if __name__ == "__main__":
    main()
