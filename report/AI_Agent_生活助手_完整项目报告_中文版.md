# AI Agent 生活助手系统 - 完整项目报告

## 项目概述

本项目是一个面向在日国际居民的多功能AI代理生活助手系统，作为硕士论文研究的核心实现。系统集成了三大核心功能：AI提醒助手、具备记忆管理的LLM问答系统，以及本地服务推荐功能。

### 技术架构
- **数据存储策略**: SQLite（热数据：对话、提醒、记忆摘要）+ YAML（冷数据：用户档案、偏好设置）
- **AI模型**: OpenAI GPT-4 / GPT-3.5-turbo
- **前端界面**: Streamlit Web UI + CLI命令行界面
- **数据库设计**: 用户管理、对话历史、记忆摘要、提醒系统四大核心表结构

## 功能实现详情

### 1. AI提醒助手
**核心特性**:
- 智能时间解析（自然语言 → 具体时间）
- 多语言支持（中文、英文、日文）
- 灵活的提醒创建方式
- 完整的CRUD操作（创建、查看、更新、删除）

**技术实现**:
```python
# 核心提醒逻辑
class ReminderAgent:
    def create_reminder(self, user_input, user_id):
        # 使用LLM解析自然语言输入
        # 提取时间、内容、优先级等信息
        # 存储到SQLite数据库
```

**CLI界面**: `cli_reminder.py` - 简洁的命令行提醒工具
**Web界面**: 集成在Streamlit应用中，提供可视化操作

### 2. LLM问答与记忆管理系统
**核心特性**:
- 多轮对话管理
- 智能记忆提取和存储
- 用户档案动态更新
- 上下文感知的回答生成

**记忆管理机制**:
- **短期记忆**: 当前对话会话中的所有消息
- **长期记忆**: 定期生成的对话摘要，存储关键信息
- **用户档案**: 从对话中提取的用户特征和偏好

**CLI界面功能**:
```bash
/new - 开始新对话
/switch <conversation_id> - 切换对话
/history - 查看对话历史
/summarize - 生成当前对话摘要
/profile - 查看用户档案
```

### 3. 本地服务推荐
**实现状态**: 基础框架已建立
**设计理念**: 基于用户档案和偏好的个性化服务推荐
**扩展方向**: 集成外部API、地理位置服务、实时数据更新

## Prompt Engineering 实验研究

### 实验设计框架
建立了业界首个面向稳定性的Prompt Engineering评估体系，包含三个核心维度：

1. **格式稳定性**: 输出格式一致性评估
2. **内容稳定性**: 基于Jaccard相似度的文本内容稳定性分析
3. **领域准确性**: 使用专业术语库的关键词准确性评估

### 实验配置
- **测试策略**: Function Calling vs Structured JSON vs Baseline
- **温度参数**: 0.0, 0.3, 0.7 三个级别
- **重复实验**: 每个配置5次迭代确保统计显著性
- **效果量化**: Cohen's d 效应量计算

### 关键实验发现

#### 综合性能排名
1. **Function Calling**: 83.2% 稳定性，97.7% 成功率（最佳综合表现）
2. **Structured JSON**: 70.4% 准确率（最高），76.3% 稳定性
3. **Baseline**: 43.1% 稳定性，68.0% 成功率（性能最低）

#### 温度参数影响
- **稳定性效应**: Cohen's d = 0.827（大效应）
- **准确性效应**: Cohen's d = 2.055（极大效应）
- **低温优势**: 温度0.0相比0.7提升15.7%稳定性

#### 统计显著性
所有主要发现均具有极大效应量（Cohen's d > 0.8），表明具有重大实际意义。

### 优化建议配置

根据实验结论，针对不同应用场景的最优配置：

| 应用场景 | 推荐策略 | 温度设置 | 优化目标 |
|---------|---------|---------|---------|
| 记忆提取 | Function Calling | 0.0 | 稳定性优先 |
| 用户档案 | Structured JSON | 0.0 | 准确性优先 |
| 提醒生成 | Function Calling | 0.1 | 稳定性+创造性平衡 |
| 问答对话 | Structured JSON | 0.2 | 准确性+自然对话 |
| 服务推荐 | Function Calling | 0.0 | 可靠性优先 |

## 数据架构设计

### SQLite数据库结构
```sql
-- 用户表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 对话表
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 记忆摘要表
CREATE TABLE memory_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    conversation_id INTEGER,
    summary TEXT,
    keywords TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 提醒表
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT NOT NULL,
    reminder_time TIMESTAMP NOT NULL,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### YAML配置管理
- **用户档案**: `user_memory.yaml` - 存储用户偏好、特征、历史交互模式
- **配置文件**: `config.py` - 系统参数、API密钥、数据库连接

## 技术创新点

### 1. 混合存储策略
- **热数据**: SQLite实现快速查询和事务处理
- **冷数据**: YAML提供灵活的配置管理和人工可读性

### 2. 多维度Prompt评估
- 首次提出稳定性导向的Prompt Engineering评估框架
- 建立了科学的效应量化方法论
- 为生产环境AI系统提供技术选择指导

### 3. 渐进式记忆管理
- 短期记忆 → 长期记忆 → 用户档案的三层架构
- 智能信息过滤和重要性评估
- 动态用户模型更新机制

## 未来发展规划

### 技术发展路线图

#### 第一阶段：RAG技术集成
- **向量数据库**: 集成Chroma/Pinecone构建知识库
- **文档处理**: 支持PDF、网页、音频等多媒体内容
- **检索优化**: 混合检索策略（关键词+语义）

#### 第二阶段：架构升级
- **微服务化**: 拆分为独立的服务模块
- **容器化部署**: Docker + Kubernetes
- **负载均衡**: 支持高并发用户访问

#### 第三阶段：功能扩展
- **多模态支持**: 图像、语音输入输出
- **实时推荐**: 基于位置的动态服务建议
- **社交功能**: 用户间经验分享平台

