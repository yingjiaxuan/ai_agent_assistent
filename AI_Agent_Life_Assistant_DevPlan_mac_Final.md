
# 🇯🇵 AI Agent Web App：在日留学生生活助手 DEMO1.0

---

## 🧠 项目目标

构建一个面向日本留学生的 AI 智能体 Web App，整合三个核心功能模块：
1. 📅 **提醒助手**：管理并智能规划事务提醒  
2. 🤖 **问答助手 + 记忆体**：具备个性化背景知识的语言交互系统  
3. 📍 **本地生活推荐**：结合日程、天气、节日等信息生成生活建议  

---

## 🧩 技术栈规划（适配 macOS）

| 模块         | 工具/库                        | 说明 |
|--------------|---------------------------------|------|
| 💻 前端 UI    | `Streamlit` ✅                 | 快速构建多页交互式界面，支持本地或在线部署 |
| 🧠 智能模型   | `OpenAI GPT-3.5` via API       | 语言理解与推理能力强，可后续替换成本地模型 |
| 📦 数据存储   | `SQLite + pandas`              | 提醒管理和用户行为日志 |
| 📓 记忆体     | `Markdown / YAML`              | 存储用户个性化背景，供 LLM 使用 |
| 🔌 外部 API   | `HolidayAPI`, `Open-Meteo` 等  | 节日、天气、推荐服务 |
| 🛠 本地配置   | `Anaconda` + `Python 3.9+`     | 适配你现有的 Python 环境 |
| 🔐 环境变量管理 | `python-dotenv`                | 读取 OpenAI API key 等私密配置 |

---

## 💻 macOS 本地环境配置步骤（首次使用指南）

1. **安装开发所需依赖（基于 Anaconda 虚拟环境）**：
```bash
pip install streamlit openai pandas sqlalchemy python-dotenv pyyaml requests
```

2. **设置 `.env` 文件（存放 OpenAI 密钥）**：
```
OPENAI_API_KEY=你的key
```

3. **运行项目主程序**：
```bash
streamlit run app.py
```

---

## 🏗 开发阶段 & 任务顺序

### 🔧 阶段一：项目初始化

| 步骤 | 内容 |
|------|------|
| 1.1 | 创建项目目录结构（见下方） |
| 1.2 | 初始化 Streamlit 页面骨架（多 Tab） |
| 1.3 | 创建 SQLite 数据库（提醒表） |
| 1.4 | 配置 `.env` 文件与 GPT API 连接测试 |

---

### 🧠 阶段二：提醒助手（Reminder Agent）

| 步骤 | 功能 | 智能行为（Agent） |
|------|------|--------------------|
| 2.1 | 添加提醒 | 输入任务内容、日期、类型 |
| 2.2 | 查看提醒 | 展示今日 + 一周提醒列表 |
| 2.3 | 智能推理提醒建议 | GPT 自动生成合理提交/准备节点（如提前3天提醒） |
| 2.4 | 状态管理 | 已完成/未完成/循环任务支持 |

---

### 🧠 阶段三：问答助手 + 记忆体（LLM + Memory Agent）

| 步骤 | 功能 | 智能行为（Agent） |
|------|------|--------------------|
| 3.1 | 问答系统接入 GPT | 实现生活咨询、日语写作、制度问答等 |
| 3.2 | 构建记忆体（自动或手动） | 提取提问内容构建 YAML/Markdown 文件 |
| 3.3 | 记忆增强问答 | 每次对话前调用记忆补全 prompt |
| 3.4 | 记忆审阅与导出 | 可查看、编辑、下载完整个人记忆摘要 |

---

### 🧠 阶段四：本地生活推荐助手（Contextual Life Agent）

| 步骤 | 功能 | 智能行为（Agent） |
|------|------|--------------------|
| 4.1 | 获取上下文信息 | 天气、节日、空闲时间段 |
| 4.2 | GPT 生成生活建议 | “你本周末可去北海道大学参加赏樱活动” |
| 4.3 | 提示推送逻辑 | 自动展示今日生活建议 / 可定时激活 |

---

## 🗂 推荐项目目录结构

```
/life_assistant_ai_agent/
├── app.py                  # 主入口，包含 Streamlit 路由
├── agents/
│   ├── reminder.py         # 提醒相关函数与 GPT 联动
│   ├── memory_agent.py     # 记忆提取与问答增强
│   └── context_agent.py    # 节日天气推荐逻辑
├── data/
│   └── reminders.db        # SQLite 数据库
├── memory/
│   └── user_memory.yaml    # 记忆内容（可人类可读）
├── utils/
│   └── prompts.py          # 所有 Prompt 模板集中管理
├── assets/                 # 图标、图片、静态文件
├── .env                    # 环境变量（API密钥）
└── README.md
```

---

## 🚀 项目展示建议

| 方式 | 用途 | 平台 |
|------|------|------|
| Streamlit Cloud 部署 | 在线演示 | https://streamlit.io/cloud |
| GitHub 项目文档 + 视频 | 简历、投递 | GitHub + YouTube |
| HuggingFace Spaces | 多语言展示 | https://huggingface.co/spaces |
| 本地打包为 `.app` | 线下展示 | `pyinstaller` 可用 |
