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

需 iOA 登录。脚本会**自动检测登录页并暂停**，等你操作完成后继续。

### 一键启动

```bash
cd game-design-methodology
./scripts/run_crawl_interactive.sh
```

或：

```bash
python3 scripts/crawl_woa_knowledge.py --start-url https://game.woa.com/knowledge/1013
```

### 操作流程

1. 脚本打开**可见浏览器**（登录状态保存在 `.browser-profile-woa/`）
2. 出现 `检测到 iOA / 登录拦截` 时停下
3. 在浏览器中完成 iOA 扫码/登录，确认知识库页面正常显示
4. 回到终端按 **Enter** 继续（脚本会再次校验）
5. 自动翻页、逐篇抓取，输出到 `raw-articles-woa/`

爬取过程中若 session 过期，会再次暂停等待登录。进度保存在 `raw-articles-woa/crawl_state.json`，中断后可续爬。

### 当前运行状态

若已在后台启动，可查看日志：

```bash
tail -f game-design-methodology/crawl.log
```

附加到 tmux 会话（在终端按 Enter 继续爬取）：

```bash
tmux -f /exec-daemon/tmux.portal.conf attach-session -t woa-knowledge-crawl
```


## 核心命题

> **游戏策划 = 将创意转化为可执行规则，并驱动玩家获得精神满足的设计者。**
>
> 一切设计服务于 **体验**；一切文档服务于 **沟通**；一切迭代服务于 **验证**。
