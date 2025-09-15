# AI Agent生活助手项目中期答辩报告（中文版）

## 项目标题
**面向跨语言支持的AI Agent：Prompt工程与多层记忆架构设计**
*Designing Prompts and Multi-Layered Memory Architecture Toward AI Agents for Cross-Lingual Support*

---

## 1. 项目背景与研究动机

### 1.1 问题背景
在日本生活的外国人（留学生、工作人员）面临诸多生活挑战：
- **语言障碍**：日语沟通能力限制了获取本地信息的效率
- **文化差异**：对日本的生活习惯、行政流程、社会规范缺乏了解
- **信息碎片化**：生活相关信息分散在各个平台，缺乏个性化整合
- **记忆负担**：需要记住大量琐碎但重要的生活细节（签证更新、医院预约等）

### 1.2 研究目标
构建一个专门面向在日外国人的AI Agent生活助手，具备：
- **个性化记忆管理**：通过多层记忆架构持续学习用户偏好和生活模式
- **跨语言支持**：支持中文、日语、英语等多语言交互
- **智能生活辅助**：提供事务提醒、智能问答、本地服务推荐三大核心功能

---

## 2. 多层记忆架构设计

### 2.1 记忆架构设计理念

我们设计了一个三层记忆架构，模拟人类的记忆机制：

**设计原则：**
- **冷热数据分离**：根据数据更新频率和访问模式分层存储
- **渐进式总结**：通过LLM自动提取和总结用户行为模式
- **个性化上下文**：为每次交互提供个性化的背景信息

### 2.2 三层记忆架构详述

#### 2.2.1 短期记忆（Short-term Memory）
**功能定位：** 存储当前对话会话中的上下文信息

**实现方式：**
```python
def _init_messages(self, is_new=True):
    self.messages = []
    if is_new:
        self.messages.append({"role": "system", "content": "You are a life assistant..."})
        if self.user_profile:
            self.messages.append({"role": "user", "content": f"[User Profile] {self.user_profile}"})
        if self.memory_summary:
            self.messages.append({"role": "user", "content": f"[Memory Summary] {self.memory_summary}"})
```

**设计理由：**
- 保持对话连贯性，避免重复询问基本信息
- 为LLM提供即时的用户背景信息
- 支持多轮对话的上下文理解

#### 2.2.2 长期记忆（Long-term Memory）
**功能定位：** 存储用户的历史对话记录和行为数据

**数据库设计：**
```sql
-- 对话历史表（热数据）
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    group_id INTEGER, -- 对话分组
    role TEXT,        -- user/assistant
    content TEXT,
    timestamp TEXT,
    tags TEXT
);

-- 记忆摘要表（热数据）
CREATE TABLE memory_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    period TEXT,
    summary TEXT,
    created_at TEXT,
    revised_by_user INTEGER,
    revised_content TEXT,
    revised_at TEXT
);
```

**设计理由：**
- 完整保存对话历史，支持用户查看和管理
- 按对话组织数据，便于检索和分析
- 支持用户手动修订记忆摘要，提高准确性

#### 2.2.3 用户画像（User Profile）
**功能定位：** 存储用户的基本信息和稳定特征

**数据结构：**
```sql
-- 用户画像表（冷数据）
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    education TEXT,
    occupation TEXT,
    city TEXT,
    interests TEXT, -- 逗号分隔
    language TEXT,  -- 逗号分隔
    nationality TEXT,
    register_date TEXT,
    last_active TEXT
);
```

**设计理由：**
- 提供稳定的用户基础信息，减少重复询问
- 支持个性化推荐和建议生成
- 作为prompt上下文的重要组成部分

### 2.3 记忆总结机制

**智能总结流程：**
1. **数据收集**：定期提取用户最近N条对话记录
2. **LLM分析**：使用专门设计的prompt让大模型分析用户行为模式
3. **结构化存储**：将总结结果存储到数据库和YAML文件
4. **用户参与**：支持用户手动编辑和精修总结内容

**核心Prompt设计：**
```python
prompt = f"""You are a smart life assistant for Japanese students/workers, please summarize the main concerns, interests, problems, action plans, habits, emotional states of the user based on the following conversation history. Please combine Japanese daily life, study, work, visa, social, health, travel, etc. themes...

Conversation history:
{history}

Please strictly output the following JSON format:
{{
  "Main Concerns": "...",
  "Interests": "...",
  "Recent Confusions": "...",
  "Action Plans": "...",
  "Living Habits": "...",
  "Emotional State": "..."
}}"""
```

---

## 3. Agent交互架构

### 3.1 整体架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                       │
│                  (Streamlit / CLI)                     │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │   Memory Agent    │
        │ - 对话管理        │
        │ - 记忆总结        │
        │ - 用户画像        │
        └─────────┬─────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼──┐    ┌────▼─────┐   ┌───▼────┐
│Reminder│   │ LLM API  │   │Life    │
│Agent   │   │(GPT-4o)  │   │Agent   │
│        │   │          │   │        │
└────────┘   └──────────┘   └────────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
        ┌─────────▼─────────┐
        │   Data Storage    │
        │ - SQLite Database │
        │ - YAML Cache      │
        └───────────────────┘
```

### 3.2 核心组件功能

**Memory Agent（记忆代理）：**
- 管理用户对话历史和上下文
- 执行定期记忆总结
- 维护用户画像信息
- 为其他Agent提供个性化上下文

**Reminder Agent（提醒代理）：**
- 智能分析待办事项优先级
- 生成个性化提醒建议
- 结合用户习惯优化提醒策略

**Life Agent（生活助手代理）：**
- 提供本地生活服务推荐
- 结合天气、节日等外部信息
- 基于用户画像个性化建议

---

## 4. 当前开发进度

### 4.1 已完成功能

✅ **项目架构搭建**
- 完整的目录结构设计
- 数据库表结构设计和初始化
- 核心类和接口定义

✅ **记忆系统核心实现**
- 多层记忆架构实现
- 对话历史管理
- 记忆自动总结功能
- 用户画像管理

✅ **基础AI交互功能**
- OpenAI API集成
- 多轮对话支持
- 命令行交互界面

✅ **数据存储系统**
- SQLite数据库实现
- YAML缓存机制
- 冷热数据分离存储

### 4.2 部分实现功能

🔄 **提醒系统**
- 基础提醒逻辑已实现
- 智能优先级分析功能开发中

🔄 **Web界面**
- Streamlit基础界面已搭建
- 功能集成和优化进行中

### 4.3 待实现功能

⏳ **本地服务推荐**
- 外部API集成（天气、节日等）
- 个性化推荐算法

⏳ **多语言支持优化**
- 语言检测和切换
- 跨语言上下文理解

⏳ **用户体验优化**
- 界面美化和交互优化
- 性能优化和错误处理

---

## 5. 技术创新点

### 5.1 Prompt工程创新
- **上下文注入策略**：将用户画像和记忆摘要作为系统级prompt注入
- **结构化输出控制**：通过精心设计的prompt确保LLM输出格式一致性
- **多语言适应性**：针对日本生活场景设计的专用prompt模板

### 5.2 记忆架构创新
- **冷热数据分离**：根据访问频率和更新频率优化存储策略
- **渐进式总结**：通过定期总结避免信息过载
- **用户参与机制**：允许用户修正和完善AI生成的记忆摘要

### 5.3 个性化交互创新
- **持续学习机制**：通过对话历史不断完善用户理解
- **场景化服务**：针对在日外国人的特定需求设计功能模块

---

## 6. 后续开发计划

### 6.1 短期目标（1-2个月）
1. **完善核心功能**：完成所有Agent的核心逻辑实现
2. **用户界面优化**：完善Web界面，提升用户体验
3. **系统集成测试**：确保各模块协同工作的稳定性

### 6.2 中期目标（3-4个月）
1. **外部API集成**：接入天气、地图、节日等第三方服务
2. **多语言支持增强**：实现更智能的语言检测和切换
3. **性能优化**：提升系统响应速度和资源利用效率

### 6.3 长期目标（5-6个月）
1. **用户测试和反馈收集**：邀请在日外国人进行实际使用测试
2. **功能扩展**：根据用户反馈增加新的服务模块
3. **论文撰写和发表准备**：整理研究成果，准备学术论文

---

## 7. 预期贡献

### 7.1 学术贡献
- 提出了针对特定用户群体的多层记忆架构设计方法
- 探索了Prompt工程在个性化AI服务中的应用
- 验证了AI Agent在跨文化生活辅助场景中的有效性

### 7.2 实用价值
- 为在日外国人提供实用的生活辅助工具
- 展示了AI技术在解决实际社会问题中的潜力
- 为类似的个性化AI服务提供了参考架构

---

## 8. 结论

本项目通过设计和实现多层记忆架构，成功构建了一个面向在日外国人的AI Agent生活助手原型系统。项目的核心创新在于：

1. **三层记忆架构**的设计有效解决了AI Agent的个性化记忆问题
2. **Prompt工程**的应用实现了高质量的个性化交互体验
3. **冷热数据分离**的存储策略平衡了性能和功能需求

目前系统的核心功能已基本实现，后续将重点完善用户体验和扩展服务功能，最终形成一个实用的生活助手系统。

---

**关键词：** AI Agent, 记忆架构, Prompt工程, 跨语言支持, 个性化服务

**项目地址：** https://github.com/[your-repo]/ai-life-assistant

**联系方式：** [your-email]@example.com
