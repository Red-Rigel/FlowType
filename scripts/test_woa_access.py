#!/usr/bin/env python3
"""Test access to game.woa.com knowledge base."""
import json
from playwright.sync_api import sync_playwright

URL = "https://game.woa.com/knowledge/1013"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(5000)
    title = page.title()
    text = page.inner_text("body")[:3000]
    html = page.content()[:5000]
    print("TITLE:", title)
    print("TEXT:", text)
    print("HTML_SNIP:", html)
    # try to find links
    links = page.eval_on_selector_all("a", "els => els.map(e => ({href: e.href, text: e.innerText}))")
    print("LINKS:", json.dumps(links[:30], ensure_ascii=False, indent=2))
    browser.close()
