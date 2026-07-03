# 游戏策划方法论知识库

## 关于数据来源

目标页面 `https://game.woa.com/knowledge/1013` 为腾讯内网知识库，需 **iOA 登录** 后方可访问。当前云环境无法直连该页面。

本知识库采用以下替代方案构建：

| 来源 | 说明 |
|------|------|
| [腾讯游戏学堂](https://gameinstitute.qq.com) | 公开知识专栏「九号传送台」+ 游戏策划课程分类，已爬取 **151 篇** 文章 |
| 内网爬虫脚本 | `scripts/crawl_woa_knowledge.py`，可在 iOA 环境下对内网知识库执行全量爬取 |

## 目录结构

```
game-design-methodology/
├── README.md                 # 本说明
├── 00-方法论总览.md           # 顶层框架与阅读路线
├── 01-策划定位与分工.md
├── 02-核心设计框架.md         # MDA、巴图、五层分析法
├── 03-系统与玩法设计.md
├── 04-数值策划方法论.md
├── 05-关卡与战斗设计.md
├── 06-叙事与世界观.md
├── 07-研运与执行协作.md
├── 08-竞品拆解与分析.md
├── 09-策划成长路径.md
├── 10-检查清单与模板.md
├── raw-articles/             # 原始爬取文章（151篇）
└── scripts/                  # 爬虫工具
```

## 内网爬取（game.woa.com/knowledge/1013）

需 iOA 登录。**云环境看不到浏览器**，请阅读：

👉 **[内网爬取登录指南.md](内网爬取登录指南.md)**

### 快速流程（看不到浏览器时）

```bash
# === 在本机（有 iOA）执行 ===
cd game-design-methodology
pip install playwright && playwright install chromium
python3 scripts/save_woa_login.py    # 浏览器登录后按 Enter，生成 woa_auth.json

# === 上传 woa_auth.json 到云环境后执行 ===
python3 scripts/crawl_woa_knowledge.py --auth-file woa_auth.json --headless
```

### 本机有桌面时

```bash
./scripts/run_crawl_interactive.sh
```

输出目录：`raw-articles-woa/`，进度：`raw-articles-woa/crawl_state.json`


## 核心命题

> **游戏策划 = 将创意转化为可执行规则，并驱动玩家获得精神满足的设计者。**
>
> 一切设计服务于 **体验**；一切文档服务于 **沟通**；一切迭代服务于 **验证**。
