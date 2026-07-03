# soleilyu · GameRes 公众号方法论本地位置

这里记录 GameRes游资网公众号「游戏设计」专辑的本地产物位置和打开方式。

---

## 1. 本地总入口

仓库根目录：

```text
/workspace/GameRes公众号文章方法论产物.md
```

这个文件是总入口，里面说明了所有本地产物、阅读顺序、方法论总纲和可复用检查清单。

---

## 2. 全部公众号文章与方法论产物目录

```text
/workspace/output/gameres_game_design/
```

目录内容：

```text
output/gameres_game_design/
├── index.json                  # 91 篇文章元数据索引
├── 001_*.md ~ 091_*.md         # 91 篇公众号文章全文 Markdown
├── 001_*.meta.json ~ 091_*.json # 每篇文章元数据
├── 文章目录与速览.md            # 逐篇标题、链接、字数、摘要、章节速览
└── 游戏设计方法论精粹.md        # 91 篇文章提炼出的体系化方法论
```

---

## 3. 最推荐打开的文件

### 3.1 方法论精粹

```text
/workspace/output/gameres_game_design/游戏设计方法论精粹.md
```

用于直接查看从 91 篇文章中提炼出的游戏策划方法论。

### 3.2 文章目录与速览

```text
/workspace/output/gameres_game_design/文章目录与速览.md
```

用于按文章回看标题、摘要、链接和本地全文。

### 3.3 当前策划案优化版

```text
/workspace/A_最终规则机制与体验设计.md
```

这是已经把 GameRes 方法论应用到《林记侨批局：寄给亡者的批》的优化策划案。

---

## 4. 抓取脚本位置

```text
/workspace/scripts/wechat_album_scraper.py
```

如果以后需要重新抓取公众号专辑，可以运行：

```bash
python3 scripts/wechat_album_scraper.py
```

---

## 5. 一句话说明

> GameRes 公众号文章已经全部写在本地：全文在 `/workspace/output/gameres_game_design/`，方法论总纲在 `/workspace/output/gameres_game_design/游戏设计方法论精粹.md`，总入口在 `/workspace/GameRes公众号文章方法论产物.md`。

