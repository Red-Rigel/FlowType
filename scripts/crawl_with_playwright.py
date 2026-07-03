#!/usr/bin/env python3
"""Playwright-based crawler for JS-rendered listings with pagination."""
import json
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "https://gameinstitute.qq.com"
OUTPUT = Path("/workspace/game-design-methodology/raw-articles")
OUTPUT.mkdir(parents=True, exist_ok=True)

PAGES = [
    f"{BASE}/knowledge",
    f"{BASE}/course/%E4%BA%A7%E5%93%81/%E6%B8%B8%E6%88%8F%E7%AD%96%E5%88%92",
]


def scroll_to_bottom(page, max_rounds=30):
    last_height = 0
    for _ in range(max_rounds):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.2)
        new_height = page.evaluate("document.body.scrollHeight")
        text = page.inner_text("body")
        if "已经到最底了" in text or new_height == last_height:
            break
        last_height = new_height


def collect_links(page) -> set[str]:
    links = page.eval_on_selector_all(
        "a[href]",
        """els => els.map(e => e.href).filter(h =>
            /\\/knowledge\\/\\d+/.test(h) ||
            /\\/course\\/detail\\/\\d+/.test(h)
        )"""
    )
    return set(links)


def extract_article_page(page, url: str) -> dict:
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)
    title = page.title().split(" - ")[0].strip()
    # Try to get main content
    selectors = ["article", ".article-content", "main", "#_app"]
    content = ""
    for sel in selectors:
        el = page.query_selector(sel)
        if el:
            content = el.inner_text()
            if len(content) > 300:
                break
    if len(content) < 300:
        content = page.inner_text("body")
    content = re.sub(r"\n{3,}", "\n\n", content)
    return {"url": url, "title": title, "content": content, "word_count": len(content)}


def main():
    all_links = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for list_url in PAGES:
            print(f"Listing: {list_url}")
            page.goto(list_url, wait_until="networkidle", timeout=90000)
            scroll_to_bottom(page)
            links = collect_links(page)
            print(f"  -> {len(links)} links")
            all_links.update(links)

        manifest = []
        for url in sorted(all_links):
            try:
                art = extract_article_page(page, url)
                if art["word_count"] < 200:
                    continue
                m = re.search(r"/(\d+)(?:\?|$)", url)
                fid = m.group(1) if m else str(abs(hash(url)))
                out = OUTPUT / f"pw_{fid}.md"
                with open(out, "w", encoding="utf-8") as f:
                    f.write(f"# {art['title']}\n\n> 来源: {art['url']}\n\n---\n\n{art['content']}")
                manifest.append({"id": fid, "title": art["title"], "url": url, "words": art["word_count"]})
                print(f"OK [{art['word_count']}]: {art['title'][:60]}")
            except Exception as e:
                print(f"ERR {url}: {e}")

        browser.close()

    with open(OUTPUT / "playwright_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Total: {len(manifest)} articles")


if __name__ == "__main__":
    main()
