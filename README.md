# wanc — 红果短剧剧本工程化工具

面向红果短剧个人创作者（编剧投稿 / AI 漫剧草稿）的**剧本专属**生产、管理与校验工具。

**只做剧本，不做视频。** 剥离绘图、配音、合成等成片能力，聚焦：
项目工程化管理、人物设定一致性（杜绝人设 OOC / 性格跳变）、提示词模板引擎、
剧本结构化解析、自动校验、版本快照与导出。

## 架构

- 后端：FastAPI + Pydantic v2 + PyYAML
- 前端：Vue 3 + Vite + Naive UI
- 交互模式（当前阶段）：**手动桥接** — 后端渲染完整 prompt，前端一键复制，
  用户粘贴到豆包桌面端生成，把返回文本粘贴回页面导入解析、校验、存版本。
  后续可新增 API 适配器实现自动生成，业务代码不变。

## 目录

```
wanc/
├── backend/app/          # FastAPI 应用
│   ├── models/           # Pydantic 数据模型
│   ├── services/         # 业务逻辑（人物/渲染/解析/校验/导出/版本）
│   ├── routers/          # REST 接口
│   └── templates/        # 内置提示词 skill 模板（yaml）
├── storage/              # 每个子目录 = 一个剧本项目实例
├── frontend/             # Vue3 前端
└── requirements.txt
```

## 启动

后端：
```bash
cd backend
python -m pip install -r ../requirements.txt
python run.py            # 或 uvicorn app.main:app --reload --port 8000
```

前端：
```bash
cd frontend
npm install
npm run dev              # 默认 http://localhost:5173
```
