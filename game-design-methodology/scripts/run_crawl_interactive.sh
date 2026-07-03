#!/usr/bin/env bash
# 启动 WOA 知识库爬虫（有界面 + iOA 手动登录）
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"

echo "=============================================="
echo "  game.woa.com 知识库爬虫"
echo "  遇到 iOA 会暂停，请在浏览器中登录后"
echo "  回到终端按 Enter 继续"
echo "=============================================="
echo ""

python3 scripts/crawl_woa_knowledge.py --start-url "https://game.woa.com/knowledge/1013"
