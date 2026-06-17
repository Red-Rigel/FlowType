# FlowType

FlowType 是一个基于Windows系统开发的基于桌面上下文的智能输入法增强系统。系统在后台提取桌面上下文关键词，并在用户使用搜狗输入法组字时通过 Alt 或停顿触发候选弹窗，结合本地模糊匹配与上下文感知查询扩展生成候选。  

初始运行时因上下文缺失，有一定时间的冷启动，属正常现象。

## Requirements

- Python
- Node.js 与 npm
- 大模型API配置：复制 `Backend/.env.example` 为 `Backend/.env`，填入API秘钥即可，目前系统的Agent设计基于Azure Open AI，出于信息安全考虑，恕不能提供开发阶段使用的API。

```powershell
pip install -r Backend/requirements.txt
pip install -r Frontend/ContextOCR/requirements.txt
pip install -r Frontend/ContextService/requirements.txt
pip install -r Frontend/ContextWordsMatching/requirements.txt
cd Frontend
npm install
```

## Run

启动前：将 `Backend/.env.example` 复制为 `Backend/.env` 并填入 API 配置。

**后端**（在仓库根目录执行）：

```powershell
cd Backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**前端**（在仓库根目录执行）：

```powershell
cd Frontend
npm run dev
```

