# 🇯🇵 AI Agent Web App：在日生活助手 DEMO1.0

## 🧠 项目目标

构建一个基于 AI Agent 架构的 Web 应用，为在日本生活的留学生、务工人员提供**事务提醒**、**智能问答与个性化记忆管理**、**本地生活服务推荐**三大智能支持，提升生活效率，减轻事务负担。

---

## 🧩 Agent 架构核心：Observe → Think → Act

| 阶段    | 描述                   | 技术手段                                  |
|---------|------------------------|-------------------------------------------|
| Observe | 感知用户输入和环境信息 | 表单输入、数据库读取、API 接口、上下文分析 |
| Think   | 分析信息、推理判断     | GPT-3.5 推理、规则触发、Prompt工程        |
| Act     | 提供行动建议与反馈     | 主动提醒、文本生成、UI 更新                |

---

## 📅 功能一：AI 提醒助手（AI Reminder Agent）

### 🎯 目标

记录 + 理解用户待办事项，主动生成合理的提醒策略，并优化任务顺序。
- 暂时假定已有提取数据的能力，利用Ai生成mock的数据进行操作

### 🔧 模块功能

| 智能阶段 | 功能说明                                     | 示例                                       |
|----------|----------------------------------------------|--------------------------------------------|
| Observe  | 记录事务 + 标注类别                          | 添加："Hitachi ES 截止 5/10"              |
| Think    | LLM 分析类别与时间，判断优先级与行动时机     | 生成："应在5/7提交推荐信，请提前准备"     |
| Act      | 主动提醒 + 输出优化日程                      | 今日提醒：结合 3 条信息，建议先完成 ES     |

---

## 🤖 功能二：LLM 问答助手 + 记忆体（LLM + Memory Agent）

### 🎯 目标

为用户提供智能回答，并自动构建个人记忆档案，用于增强个性化推荐与上下文推理。

- 个性化存储的实现 （回答中要体现已经存储到了用户信息，类似于 UI输出，识别到你是XXX，拥有XXX基本信息，若要查看详细信息，请点击以下link）
  1. 存储格式，存储位置（Client or Server）
- 个性化存储的更新周期——一周？两周？，存储的优先级
- 用户画像的关键词——比如 年龄，学历，职业，身份等（这个应该比较重要，类似于生成一个简单的个人CV）
- 如何使用个性化存储--RAG
  1. 使用全量（或部分周期内）记忆按钮

- 初次使用，询问用户个人信息等（这部分还需要细化）

### 🔧 模块功能

| 智能阶段 | 功能说明                                         | 示例                                       |
|----------|--------------------------------------------------|--------------------------------------------|
| Observe  | 记录提问与回答内容摘要                           | 问："我要怎么写实习邮件？"               |
| Think    | 结合记忆信息（如专业、学校）增强 Prompt          | 回答："你的信息化学背景可强调建模经验"   |
| Act      | 输出个性化回答；可定期生成记忆文档 + 自动提醒回顾 | "记得更新你在 Hitachi 面试的进展"         |

---

## 📍 功能三：本地服务推荐助手（Contextual Life Agent）

### 🎯 目标

结合时间、地理、日程，为用户提供节日、天气、短途旅行等生活建议。
- 定周期，后台自动使用api进行格式化询问

### 🔧 模块功能

| 智能阶段 | 功能说明                                           | 示例                                         |
|----------|----------------------------------------------------|----------------------------------------------|
| Observe  | 感知位置、天气、节日、用户日程                     | 地点：札幌，天气：晴，黄金周临近             |
| Think    | 判断用户空闲时间、节日机会                         | 判断周末无任务，推断适合短途活动             |
| Act      | 生成推荐："北大赏樱节本周开放，适合周末参加"      | 并附上地图/交通/活动链接                     |

---

## 🧱 系统结构图

- Tab1: Chatbot对话框（含查看 个人档案 按钮/功能）
- Tab2: Reminder按钮（含Life Recommendation）


```
            +---------------------+
            |  User Interface     |
            |  (Streamlit Tabs)   |
            +---------------------+
                    ↓           ↓
+---------------------+    +-------------------+
| Reminder Agent      |    | LLM+Memory Agent  |
| - 分类任务           |     | - 记录提问        |
| - 时间策略建议        |    | - 个性化回复      |
| - 合并事务提醒        |    | - 生成记忆摘要    |
+---------------------+   +-------------------+
                    ↓           ↓
                 +------------------------+
                 |  Contextual Life Agent |
                 | - 节日天气活动推荐     |
                 | - 结合日程智能推送     |
                 +------------------------+
```

---

## 🔧 技术栈

| 模块       | 技术                           |
|------------|--------------------------------|
| 前端 UI    | Streamlit                      |
| 后端语言   | Python                         |
| 智能模块   | OpenAI GPT-3.5（可换成本地模型）|
| 存储       | SQLite + Markdown/YAML 记忆文档 |
| 第三方 API | 天气 API、节日 API（如 HolidayAPI）等 |

---

## ✍️ 可写入简历描述

> Built a personalized AI Agent web app to support international student life in Japan. The system integrates daily reminder planning, contextual Q&A with memory-augmented LLM, and local service recommendations. Enabled agent-based behavior by embedding GPT-3.5 for task prioritization, knowledge summarization, and lifestyle suggestions based on personal context.

## 📂 推荐项目目录结构与主要脚本说明

以下为建议的项目目录结构及主要.py脚本的注释模板，便于后续开发和维护：

```
life_assistant_ai_agent/
│
├── app.py
├── README.md
│
├── agents/
│   ├── __init__.py
│   ├── reminder_agent.py         # AI提醒助手核心逻辑
│   ├── memory_agent.py           # LLM问答+记忆体核心逻辑
│   └── life_agent.py             # 本地服务推荐助手核心逻辑
│
├── utils/
│   ├── __init__.py
│   ├── api_utils.py              # 第三方API调用工具
│   ├── time_utils.py             # 时间/日期处理工具
│   └── text_utils.py             # 文本处理、Prompt等工具
│
├── data/
│   ├── mock_tasks.json           # 示例/测试用的mock数据
│   └── database.db               # SQLite数据库（可后续生成）
│
├── memory/
│   ├── __init__.py
│   ├── user_profile.py           # 用户画像/信息管理
│   ├── memory_store.py           # 记忆体存储与检索
│   └── memory_docs/              # 记忆文档（如Markdown/YAML）
│
├── assets/
│   └── (images, icons, etc.)
│
├── config.py                     # 配置文件（API Key、路径等）
└── tests/
    ├── __init__.py
    ├── test_reminder_agent.py
    ├── test_memory_agent.py
    └── test_life_agent.py
```

---

### 主要.py脚本模板（含注释）

#### agents/reminder_agent.py
```python
"""
AI提醒助手：负责任务的记录、分类、优先级分析与提醒策略。
"""
class ReminderAgent:
    def __init__(self):
        pass
    def add_task(self, task):
        """添加新任务"""
        pass
    def analyze_tasks(self):
        """分析任务优先级与提醒时机"""
        pass
    def get_reminders(self):
        """生成今日/近期提醒"""
        pass
```

#### agents/memory_agent.py
```python
"""
LLM问答+记忆体：负责智能问答、个性化记忆管理与调用。
"""
class MemoryAgent:
    def __init__(self):
        pass
    def record_interaction(self, question, answer):
        """记录用户问答内容摘要"""
        pass
    def update_user_profile(self, info):
        """更新用户画像信息"""
        pass
    def personalized_reply(self, question):
        """结合记忆体生成个性化回答"""
        pass
```

#### agents/life_agent.py
```python
"""
本地服务推荐助手：结合时间、地理、日程，推送本地生活建议。
"""
class LifeAgent:
    def __init__(self):
        pass
    def fetch_local_info(self, location):
        """获取本地天气、节日等信息"""
        pass
    def recommend_activity(self, user_schedule):
        """根据用户日程推荐活动"""
        pass
```

#### utils/api_utils.py
```python
"""
第三方API调用工具，如天气、节日等。
"""
def get_weather(location):
    pass
def get_holiday(date, country='JP'):
    pass
```

#### utils/time_utils.py
```python
"""
时间/日期处理工具。
"""
def parse_date(date_str):
    pass
def get_today():
    pass
```

#### utils/text_utils.py
```python
"""
文本处理、Prompt工程等工具。
"""
def summarize_text(text):
    pass
def generate_prompt(context):
    pass
```

#### memory/user_profile.py
```python
"""
用户画像信息管理。
"""
class UserProfile:
    def __init__(self):
        pass
    def update_profile(self, info):
        pass
    def get_profile(self):
        pass
```

#### memory/memory_store.py
```python
"""
记忆体存储与检索。
"""
class MemoryStore:
    def __init__(self):
        pass
    def save_memory(self, memory):
        pass
    def retrieve_memory(self, query):
        pass
```

#### config.py
```python
"""
全局配置文件：API Key、数据库路径等。
"""
OPENAI_API_KEY = "your-openai-key"
DATABASE_PATH = "data/database.db"
```

#### tests/test_reminder_agent.py
```python
import unittest
from agents.reminder_agent import ReminderAgent
class TestReminderAgent(unittest.TestCase):
    def test_add_task(self):
        agent = ReminderAgent()
        # 测试添加任务
        self.assertIsNone(agent.add_task("Test Task"))
if __name__ == "__main__":
    unittest.main()
```

---
