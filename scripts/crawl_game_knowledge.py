#!/usr/bin/env python3
"""Crawl Tencent Game Institute knowledge articles for game design planning."""
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://gameinstitute.qq.com"
OUTPUT = Path("/workspace/game-design-methodology/raw-articles")
OUTPUT.mkdir(parents=True, exist_ok=True)

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
})

# Seed URLs: knowledge column + game planning course category
SEED_LIST_PAGES = [
    f"{BASE}/knowledge",
    f"{BASE}/course/%E4%BA%A7%E5%93%81/%E6%B8%B8%E6%88%8F%E7%AD%96%E5%88%92",
]

# Known high-value planning articles (from search + listing)
KNOWN_ARTICLE_IDS = [
    "100043",  # 做数值就是做体验
    "100042", "100122", "100015",
]

PLANNING_KEYWORDS = re.compile(
    r"策划|数值|系统|关卡|战斗|设计|玩法|体验|文案|世界观|IP|运营|成长|经济|平衡|MOBA|FPS|SLG|MMO|RPG"
)


def fetch(url: str, retries: int = 3) -> str:
    for i in range(retries):
        try:
            r = SESSION.get(url, timeout=30)
            r.raise_for_status()
            r.encoding = r.apparent_encoding or "utf-8"
            return r.text
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(1 + i)
    return ""


def extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full = urljoin(base_url, href)
        if re.search(r"/knowledge/\d+", full):
            links.add(full.split("?")[0])
        if re.search(r"/course/detail/\d+", full):
            links.add(full.split("?")[0])
        if re.search(r"/community/detail/\d+", full):
            links.add(full.split("?")[0])
    return sorted(links)


def extract_article(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    if not title:
        t = soup.find("title")
        title = t.get_text(strip=True) if t else url

    # Main content areas
    content_parts = []
    for sel in ["article", ".article-content", ".m-article", ".content", "main"]:
        el = soup.select_one(sel)
        if el:
            content_parts.append(el.get_text("\n", strip=True))
            break
    if not content_parts:
        # fallback: body text minus nav
        body = soup.find("body")
        if body:
            for tag in body.find_all(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            content_parts.append(body.get_text("\n", strip=True))

    content = "\n\n".join(content_parts)
    # Clean excessive whitespace
    content = re.sub(r"\n{3,}", "\n\n", content)

    author = ""
    for p in soup.find_all(["p", "span", "div"]):
        txt = p.get_text(strip=True)
        if "腾讯" in txt and ("策划" in txt or "互娱" in txt) and len(txt) < 80:
            author = txt
            break

    return {
        "url": url,
        "title": title,
        "author": author,
        "content": content,
        "word_count": len(content),
    }


def paginate_knowledge() -> list[str]:
    """Use playwright-rendered listing if needed; fallback to static parse."""
    all_links = set()
    for seed in SEED_LIST_PAGES:
        try:
            html = fetch(seed)
            all_links.update(extract_links(html, seed))
        except Exception as e:
            print(f"WARN seed {seed}: {e}")

    # Add known articles
    for aid in KNOWN_ARTICLE_IDS:
        all_links.add(f"{BASE}/knowledge/{aid}")

    return sorted(all_links)


def main():
    print("Collecting article links...")
    links = paginate_knowledge()
    print(f"Found {len(links)} links from seeds")

    # Filter planning-related from knowledge URLs
    articles = []
    manifest = []

    for url in links:
        try:
            html = fetch(url)
            art = extract_article(html, url)
            if art["word_count"] < 200:
                print(f"SKIP (too short): {url}")
                continue
            if "/knowledge/" in url or PLANNING_KEYWORDS.search(art["title"] + art["content"][:500]):
                articles.append(art)
                slug = re.search(r"/(\d+)$", url)
                fname = slug.group(1) if slug else str(abs(hash(url)))
                out = OUTPUT / f"{fname}.md"
                with open(out, "w", encoding="utf-8") as f:
                    f.write(f"# {art['title']}\n\n")
                    f.write(f"> 来源: {art['url']}\n")
                    if art["author"]:
                        f.write(f"> 作者: {art['author']}\n")
                    f.write("\n---\n\n")
                    f.write(art["content"])
                manifest.append({"id": fname, "title": art["title"], "url": url, "words": art["word_count"]})
                print(f"OK: {art['title'][:50]} ({art['word_count']} chars)")
            time.sleep(0.5)
        except Exception as e:
            print(f"ERR {url}: {e}")

    with open(OUTPUT / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(articles)} articles to {OUTPUT}")


if __name__ == "__main__":
    main()
