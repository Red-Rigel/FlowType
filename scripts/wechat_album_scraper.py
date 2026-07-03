#!/usr/bin/env python3
"""Scrape WeChat public account album articles and extract text content."""

import json
import re
import time
import html
import urllib.request
from pathlib import Path
from html.parser import HTMLParser

ALBUM_URL = (
    "https://mp.weixin.qq.com/mp/appmsgalbum"
    "?__biz=MjM5NTMxNTU0MQ==&action=getalbum"
    "&album_id=2331556882131320832&count=20&is_reverse=0&f=json"
)
OUTPUT_DIR = Path("output/gameres_game_design")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def fetch(url: str, retries: int = 3) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
            print(f"  retry {attempt + 1} for {url}: {exc}")
    return ""


def fetch_all_articles() -> list[dict]:
    articles: list[dict] = []
    seen: set[str] = set()
    url = ALBUM_URL

    while url:
        raw = fetch(url)
        data = json.loads(raw)
        resp = data["getalbum_resp"]
        batch = resp.get("article_list", [])
        for item in batch:
            key = item.get("key") or f"{item['msgid']}_{item['itemidx']}"
            if key in seen:
                continue
            seen.add(key)
            articles.append(
                {
                    "title": item["title"],
                    "url": item["url"],
                    "create_time": int(item.get("create_time", 0)),
                    "msgid": item["msgid"],
                    "itemidx": item["itemidx"],
                    "key": key,
                }
            )

        if resp.get("continue_flag") != "1" or not batch:
            break

        last = batch[-1]
        url = (
            "https://mp.weixin.qq.com/mp/appmsgalbum"
            f"?__biz=MjM5NTMxNTU0MQ==&action=getalbum"
            f"&album_id=2331556882131320832&count=20&is_reverse=0&f=json"
            f"&begin_msgid={last['msgid']}&begin_itemidx={last['itemidx']}"
        )
        time.sleep(0.4)

    return articles


class WeChatArticleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_content = False
        self.depth = 0
        self.parts: list[str] = []
        self.title = ""
        self.in_title = False
        self.skip_tags = {"script", "style", "noscript"}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "h1" and attrs_dict.get("class") == "rich_media_title":
            self.in_title = True
            return

        cls = attrs_dict.get("class") or ""
        if tag == "div" and "rich_media_content" in cls:
            self.in_content = True
            self.depth = 1
            return

        if self.in_content:
            self.depth += 1
            if tag in {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote"}:
                self.parts.append("\n")
            if tag == "br":
                self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self.in_title and tag == "h1":
            self.in_title = False
            return

        if self.in_content:
            if tag in {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote"}:
                self.parts.append("\n")
            self.depth -= 1
            if self.depth <= 0:
                self.in_content = False

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        if self.in_title:
            self.title += text
        elif self.in_content:
            self.parts.append(text)


def extract_article_text(page_html: str) -> tuple[str, str]:
    # Try js_content variable first (often more complete)
    m = re.search(r'var\s+msg_title\s*=\s*"([^"]*)"', page_html)
    title = html.unescape(m.group(1)) if m else ""

    content_match = re.search(
        r'<div class="rich_media_content[^"]*"[^>]*>(.*?)</div>\s*<script',
        page_html,
        re.S,
    )
    if content_match:
        content_html = content_match.group(1)
        text = re.sub(r"<br\s*/?>", "\n", content_html, flags=re.I)
        text = re.sub(r"</p>", "\n\n", text, flags=re.I)
        text = re.sub(r"</h[1-6]>", "\n\n", text, flags=re.I)
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if len(text) > 200:
            return title, text

    parser = WeChatArticleParser()
    parser.feed(page_html)
    if not title:
        title = parser.title.strip()
    text = re.sub(r"\s+\n", "\n", "".join(parser.parts))
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return title, text


def slugify(title: str, idx: int) -> str:
    safe = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", title)[:60].strip("_")
    return f"{idx:03d}_{safe or 'article'}"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching album article list...")
    articles = fetch_all_articles()
    articles.sort(key=lambda x: x["create_time"], reverse=True)
    print(f"Found {len(articles)} articles")

    index: list[dict] = []
    for i, art in enumerate(articles, 1):
        slug = slugify(art["title"], i)
        out_path = OUTPUT_DIR / f"{slug}.md"
        meta_path = OUTPUT_DIR / f"{slug}.meta.json"

        if out_path.exists() and out_path.stat().st_size > 500:
            print(f"[{i}/{len(articles)}] skip existing: {art['title'][:40]}")
            index.append({**art, "slug": slug, "status": "cached"})
            continue

        print(f"[{i}/{len(articles)}] fetching: {art['title'][:50]}")
        try:
            page = fetch(art["url"])
            title, text = extract_article_text(page)
            if not title:
                title = art["title"]

            if "环境异常" in page or "完成验证" in page or len(text) < 100:
                status = "blocked_or_short"
                text = text or "CONTENT_BLOCKED_OR_EMPTY"
            else:
                status = "ok"

            body = (
                f"# {title}\n\n"
                f"- 来源: {art['url']}\n"
                f"- 发布时间戳: {art['create_time']}\n\n"
                f"---\n\n{text}\n"
            )
            out_path.write_text(body, encoding="utf-8")
            meta_path.write_text(
                json.dumps({**art, "status": status, "chars": len(text)}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            index.append({**art, "slug": slug, "status": status, "chars": len(text)})
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR: {exc}")
            index.append({**art, "slug": slug, "status": f"error: {exc}"})

        time.sleep(0.8)

    (OUTPUT_DIR / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Done. Index saved to {OUTPUT_DIR / 'index.json'}")


if __name__ == "__main__":
    main()
