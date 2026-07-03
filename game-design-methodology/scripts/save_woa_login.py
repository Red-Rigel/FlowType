#!/usr/bin/env python3
"""
在本机（已安装 iOA、能访问 game.woa.com）运行此脚本，导出登录状态。

步骤:
  1. pip install playwright && playwright install chromium
  2. python3 save_woa_login.py
  3. 在弹出的浏览器中完成 iOA 登录，直到看到知识库页面
  4. 回到终端按 Enter
  5. 生成 woa_auth.json — 上传到云环境或在本机直接爬取

用法:
  python3 save_woa_login.py
  python3 save_woa_login.py -o /path/to/woa_auth.json
"""
from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

DEFAULT_URL = "https://game.woa.com/knowledge/1013"
DEFAULT_OUT = Path(__file__).resolve().parent.parent / "woa_auth.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="在本机导出 game.woa.com 登录状态")
    parser.add_argument("--url", default=DEFAULT_URL, help="登录后要确认的页面")
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUT, help="输出文件")
    args = parser.parse_args()

    print("=" * 60)
    print("  本机 iOA 登录导出工具")
    print("=" * 60)
    print(f"目标页面: {args.url}")
    print(f"输出文件: {args.output}")
    print()
    print("即将打开浏览器，请完成 iOA 登录。")
    print("看到知识库正常内容后，回到终端按 Enter 保存登录状态。")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1400, "height": 900}, locale="zh-CN")
        page = context.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=120000)

        input("\n>>> 已在浏览器中完成 iOA 登录并看到知识库？按 Enter 保存: ")

        text = page.inner_text("body")[:2000]
        if "访问失败" in text or "iOA" in text and "下载" in text:
            print("警告: 页面仍像未登录状态，但会照常保存当前 Cookie。")
            print("若后续爬取失败，请重新运行本脚本。")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(args.output))
        browser.close()

    print(f"\n✓ 已保存: {args.output}")
    print()
    print("下一步（任选其一）:")
    print("  A) 本机直接爬取:")
    print(f"     python3 scripts/crawl_woa_knowledge.py --auth-file {args.output} --headless")
    print("  B) 上传到云环境后爬取:")
    print(f"     将 {args.output.name} 放到 game-design-methodology/ 目录")
    print("     python3 scripts/crawl_woa_knowledge.py --auth-file woa_auth.json --headless")


if __name__ == "__main__":
    main()
