# 写入本机 `~/Projects` 目录说明

你提到的终端位置是：

```bash
soleilyu@SOLEILYU-MB0 Projects %
```

也就是你自己 Mac 电脑上的：

```bash
~/Projects
```

当前我所在环境是 Cursor Cloud 的远程机器：

```bash
/workspace
```

因此我不能直接把文件写进你 Mac 本机的 `~/Projects`，但我已经把所有产物提交并推送到 Git 仓库。你只需要在本机终端执行下面命令，就能把这些文件同步到你的电脑。

---

## 方式一：你本机已经有这个仓库

在你的 Mac 终端执行：

```bash
cd ~/Projects/FlowType
git pull
```

拉取后，本机将出现这些文件：

```text
~/Projects/FlowType/GameRes公众号文章方法论产物.md
~/Projects/FlowType/soleilyu.md
~/Projects/FlowType/A_最终规则机制与体验设计.md
~/Projects/FlowType/output/gameres_game_design/
```

最重要的方法论文件在：

```text
~/Projects/FlowType/output/gameres_game_design/游戏设计方法论精粹.md
```

91 篇文章全文在：

```text
~/Projects/FlowType/output/gameres_game_design/
```

---

## 方式二：你本机还没有这个仓库

在你的 Mac 终端执行：

```bash
cd ~/Projects
git clone https://github.com/Red-Rigel/FlowType.git
```

然后打开：

```bash
cd ~/Projects/FlowType
```

本地产物位置同样是：

```text
~/Projects/FlowType/output/gameres_game_design/
```

---

## 方式三：复制成一个单独的本机资料夹

如果你不想每次进入项目目录，也可以在本机拉取仓库后，把方法论产物复制到独立目录：

```bash
cd ~/Projects/FlowType
mkdir -p ~/Projects/GameRes公众号方法论
cp GameRes公众号文章方法论产物.md ~/Projects/GameRes公众号方法论/
cp soleilyu.md ~/Projects/GameRes公众号方法论/
cp A_最终规则机制与体验设计.md ~/Projects/GameRes公众号方法论/
cp -R output/gameres_game_design ~/Projects/GameRes公众号方法论/
```

复制完成后，你电脑里的独立资料夹就是：

```text
~/Projects/GameRes公众号方法论/
```

里面会有：

```text
GameRes公众号文章方法论产物.md
soleilyu.md
A_最终规则机制与体验设计.md
gameres_game_design/
```

---

## 最短命令

如果你本机已有仓库，直接执行：

```bash
cd ~/Projects/FlowType && git pull
```

然后打开：

```text
~/Projects/FlowType/output/gameres_game_design/游戏设计方法论精粹.md
```

