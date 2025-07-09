# Prompt Engineering实验说明文档

## 📋 实验概述

本目录包含用于测试不同Prompt设计方案和OpenAI API参数对输出质量影响的实验代码。

### 🧪 实验脚本

- **`test_prompt_experiments.py`**: 主要Prompt Engineering实验脚本
- **`test_prompt_stability.py`**: **新增**稳定性和准确性测试（重复实验）
- **`analyze_experiment_results.py`**: 结果分析和可视化脚本  
- **`demo_expected_results.py`**: 理论结果演示脚本

### 🎯 实验目标

1. **Prompt设计对比**：测试三种不同的Prompt模式：
   - `baseline`: 基础自由文本提示（项目当前使用的方式）
   - `structured`: 结构化JSON模板提示（明确指定输出格式）
   - `function_calling`: OpenAI函数调用模式（原生结构化输出）

2. **API参数优化**：测试不同temperature和top_p组合对输出稳定性的影响

3. **质量评估**：评估JSON解析成功率、字段完整性、输出一致性等指标

## 🚀 快速开始

### 前置要求

```bash
# 确保已安装依赖
pip install openai python-dotenv

# 可选：安装可视化依赖
pip install matplotlib pandas
```

### 运行实验

```bash
# 1. 切换到项目根目录
cd Code/life_assistant_ai_agent

# 2. 确保.env文件包含OpenAI API Key
echo "OPENAI_API_KEY=your_api_key_here" >> .env

# 3. 运行Prompt Engineering实验（格式测试）
python tests/test_prompt_experiments.py

# 4. 运行稳定性和准确性测试（新增）
python tests/test_prompt_stability.py

# 5. 分析实验结果
python tests/analyze_experiment_results.py
```

## 📊 实验设计

### 测试参数网格

| 维度 | 取值 | 说明 |
|------|------|------|
| **Prompt类型** | baseline, structured, function_calling | 三种不同的设计理念 |
| **Temperature** | 0.0, 0.3, 0.7 | 从确定性到创造性的梯度 |
| **Top-p** | 0.8, 1.0 | 核采样参数 |

总计：**3 × 3 × 2 = 18** 次API调用

### 评估指标

1. **JSON解析成功率**：输出是否为有效的JSON格式
2. **字段完整性**：必需字段的存在情况
3. **内容质量**：字段是否为空或无意义
4. **输出长度**：响应文本的长度统计
5. **一致性**：相同参数下的输出稳定性

## 📁 输出文件

实验完成后，会在`tests/experiment_results/`目录下生成：

```
experiment_results/
├── prompt_comparison_results.csv      # 主要结果数据
├── analysis_report.txt               # 详细分析报告
├── analysis_charts.png              # 可视化图表（可选）
└── raw_responses/                    # 原始LLM响应
    ├── 20241201_143022_baseline_temp0.0_top_p0.8.txt
    ├── 20241201_143022_structured_temp0.0_top_p0.8.txt
    └── ...
```

## 📈 结果分析

### CSV数据字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `experiment_id` | string | 实验批次ID |
| `prompt_type` | string | Prompt类型 |
| `temperature` | float | 温度参数 |
| `top_p` | float | top-p参数 |
| `json_parseable` | boolean | 是否能解析为JSON |
| `required_fields_present` | int | 存在的必需字段数量 |
| `field_completeness_rate` | float | 字段完整率（0-1） |
| `response_length` | int | 响应长度（字符数） |
| `empty_fields_count` | int | 空字段数量 |
| `raw_file_path` | string | 原始响应文件路径 |

### 预期结果模式

根据Prompt Engineering理论，预期结果：

1. **Function Calling** > **Structured JSON** > **Baseline** （成功率）
2. **低Temperature**（0.0-0.3）比**高Temperature**（0.7）更稳定
3. **top_p=0.8** 比 **top_p=1.0** 更一致

## 🔧 自定义实验

### 修改实验参数

编辑`test_prompt_experiments.py`中的常量：

```python
# 修改测试的用户和消息数量
TARGET_USER_ID = 2  # 改为测试李四的数据
N_MESSAGES_TO_FETCH = 50  # 增加上下文长度

# 修改API参数范围
temperature_values = [0.0, 0.1, 0.2, 0.5]  # 更精细的温度测试
top_p_values = [0.7, 0.8, 0.9, 1.0]       # 更多的top_p取值
```

### 添加新的Prompt模式

在`test_prompt_experiments.py`中添加新的模板：

```python
# 添加新的Prompt模板
NEW_TEMPLATE = """
Your custom prompt template here...
{conversation_history}
"""

# 添加新的执行函数
def execute_new_prompt(conversation_history: str, temperature: float, top_p: float) -> str:
    # 实现你的新Prompt逻辑
    pass

# 在main()函数中添加到prompt_types列表
prompt_types = ["baseline", "structured", "function_calling", "new_prompt"]
```

### 测试其他任务

当前实验专注于**记忆摘要生成**任务。要测试其他任务（如用户画像生成、智能提醒），可以：

1. 复制`test_prompt_experiments.py`并重命名
2. 修改`REQUIRED_JSON_FIELDS`为对应任务的字段
3. 更新Prompt模板为对应任务的指令
4. 调整评估指标

## 🎛️ 高级使用

### 批量测试多个用户

```python
# 修改main()函数，循环测试多个用户
for user_id in [1, 2]:  # 测试张三和李四
    TARGET_USER_ID = user_id
    conversation_history = fetch_conversation_history(user_id, N_MESSAGES_TO_FETCH)
    # ... 运行实验
```

### 统计显著性测试

对于更严格的学术评估，可以：

1. 增加重复实验次数（每组参数运行5-10次）
2. 添加统计检验（t-test, ANOVA）
3. 计算置信区间

### 成本控制

每次完整实验需要18次API调用。要控制成本：

```python
# 减少参数组合
temperature_values = [0.0, 0.7]  # 只测试极端值
top_p_values = [1.0]             # 固定top_p

# 或使用采样而非全网格搜索
import random
param_combinations = list(itertools.product(prompt_types, temperature_values, top_p_values))
selected_combinations = random.sample(param_combinations, 10)  # 随机选择10组
```

## 📚 参考资料

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Best Practices for Prompt Engineering](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api)
- [Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)

## 🔄 稳定性和准确性测试（新增功能）

### 概述

`test_prompt_stability.py`专门测试**相同数据、相同问题**下不同Prompt设计的**内容稳定性和准确性**，补充了原实验只关注格式正确性的不足。

### 测试方法

1. **重复实验**：每个参数组合重复5次，测试输出一致性
2. **语义相似度**：使用Jaccard相似度计算文本内容重叠度
3. **关键词准确性**：基于预期关键词评估内容质量
4. **稳定性量化**：计算变异系数来量化输出稳定性

### 核心评估指标

| 指标类型 | 具体指标 | 说明 |
|----------|----------|------|
| **稳定性** | 平均相似度 | 多次输出间的平均文本相似度 |
| **稳定性** | 最小/最大相似度 | 相似度的变化范围 |
| **稳定性** | 稳定性分数 | 综合考虑相似度和变异度的评分 |
| **准确性** | 关键词匹配率 | 输出中包含预期关键词的比例 |
| **格式** | JSON成功率 | 结构化输出的格式正确性 |

### 运行稳定性测试

```bash
# 运行稳定性实验（约30次API调用）
python tests/test_prompt_stability.py

# 查看结果
ls tests/stability_results/
# ├── stability_analysis_report.txt    # 详细分析报告
# ├── stability_results.csv           # 数据结果
# └── ...
```

### 实验配置

```python
# 可调整的参数
N_REPETITIONS = 5  # 每组参数重复次数（建议3-10次）
TARGET_USER_ID = 1  # 测试用户
N_MESSAGES_TO_FETCH = 30  # 对话历史长度

# 测试的参数组合（简化版本，专注稳定性）
test_configs = [
    {"temperature": 0.0, "top_p": 0.8},  # 最稳定配置
    {"temperature": 0.7, "top_p": 1.0}   # 最随机配置
]
```

### 预期关键词库

系统会根据任务特点自动检测输出内容中的相关关键词：

```python
EXPECTED_KEYWORDS = {
    "Main_Concerns": ["tokyo", "activity", "weather", "outdoor", "local"],
    "Interests": ["cherry", "blossom", "sakura", "festival", "tourism"],
    "Recent_Problems": ["reservation", "booking", "process", "unfamiliar"],
    "Action_Plans": ["attend", "participate", "visit", "reserve", "plan"],
    "Emotional_State": ["interest", "enthusiastic", "eager", "positive"]
}
```

### 报告示例

稳定性测试会生成如下格式的分析报告：

```
🔬 Prompt Stability and Accuracy Analysis Report
==========================================
📊 Total Configurations Tested: 6
🔄 Repetitions per Configuration: 5
📅 Generated: 2024-12-01 14:30:22

🏆 Top Performers by Stability:
1. function_calling (temp=0.0, top_p=0.8)
   Stability: 0.874 | Accuracy: 0.672

🎯 Top Performers by Accuracy:
1. structured (temp=0.0, top_p=0.8)
   Accuracy: 0.701 | Stability: 0.823

💡 Key Findings:
• Best Overall Configuration: function_calling with temp=0.0, top_p=0.8
• Combined Score: 1.546
• Low temperature generally improves stability
• Function calling shows highest consistency in structured output
```

### 与主实验的对比

| 实验类型 | `test_prompt_experiments.py` | `test_prompt_stability.py` |
|----------|------------------------------|----------------------------|
| **测试重点** | 格式正确性 | 内容稳定性和准确性 |
| **API调用次数** | 18次（单次） | 30次（5次重复×6组） |
| **输出指标** | JSON解析率、字段完整性 | 文本相似度、关键词匹配 |
| **适用场景** | 快速格式验证 | 深度内容质量评估 |

## 🐛 故障排除

### 常见问题

1. **API Key错误**
   ```
   ❌ OPENAI_API_KEY not found in .env file
   ```
   确保`.env`文件在项目根目录且包含有效的API Key

2. **数据库连接失败**
   ```
   ❌ Error fetching conversation history
   ```
   确保运行了`python init_database.py`初始化数据库

3. **无对话历史**
   ```
   ❌ No valid conversation history found
   ```
   确保数据库中有用户对话记录，或运行CLI工具生成一些对话

4. **导入错误**
   ```
   ModuleNotFoundError: No module named 'config'
   ```
   确保在项目根目录运行脚本

### 调试模式

在脚本开头添加调试输出：

```python
DEBUG = True

if DEBUG:
    print(f"Database path: {DATABASE_PATH}")
    print(f"Conversation history preview: {conversation_history[:200]}...")
```

## 💡 实验扩展建议

1. **多模型对比**：扩展支持Claude、Gemini等其他LLM
2. **多语言测试**：测试中文、日文Prompt的效果差异
3. **上下文长度影响**：测试不同对话历史长度的影响
4. **Few-shot学习**：添加示例输入输出到Prompt中
5. **Chain-of-Thought**：测试思维链Prompt的效果 