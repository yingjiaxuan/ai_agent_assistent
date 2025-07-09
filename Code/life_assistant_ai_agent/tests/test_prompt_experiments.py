# -*- coding: utf-8 -*-
"""
Prompt Engineering Experiment Script
====================================
本脚本用于对比不同的Prompt设计方案和OpenAI API参数对结果质量的影响。

实验目标：
1. 测试三种不同的Prompt设计模式：
   - baseline: 基础自由文本提示
   - structured: 结构化JSON模板提示
   - function_calling: OpenAI函数调用模式
2. 测试不同的API参数组合(temperature, top_p)对输出稳定性的影响
3. 评估输出的JSON格式正确性和内容完整性

实验数据源：项目数据库中的真实对话历史
评估指标：JSON解析成功率、必需字段完整性、输出长度一致性

使用方法：
cd Code/life_assistant_ai_agent
python tests/test_prompt_experiments.py
"""

import os
import re
import csv
import json
import sqlite3
import itertools
from datetime import datetime
from pathlib import Path
import sys

# 导入依赖库
from dotenv import load_dotenv
import openai

# ============================================================================
# 1. 环境配置和导入项目模块
# ============================================================================

# 加载环境变量
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY not found in .env file. Please add it first.")

# 配置OpenAI客户端（使用新版本API格式）
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# 动态导入项目配置（处理不同的运行环境）
try:
    # 当作为模块运行时: python -m life_assistant_ai_agent.tests.test_prompt_experiments
    from ..config import DATABASE_PATH
except ImportError:
    # 当直接运行时: python tests/test_prompt_experiments.py
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))
    from config import DATABASE_PATH

# ============================================================================
# 2. 实验配置常量
# ============================================================================

# 实验参数配置
N_MESSAGES_TO_FETCH = 30  # 从数据库提取的对话条数
TARGET_USER_ID = 1        # 目标用户ID（使用mock数据中的张三）

# JSON输出的必需字段（基于项目需求定义）
REQUIRED_JSON_FIELDS = [
    "Main_Concerns",      # 主要关注点
    "Interests",          # 兴趣爱好  
    "Recent_Problems",    # 近期困惑
    "Action_Plans",       # 行动计划
    "Emotional_State"     # 情绪状态
]

# 输出文件路径配置
RESULTS_DIR = Path(__file__).parent / "experiment_results"
RESULTS_DIR.mkdir(exist_ok=True)

RESULTS_CSV = RESULTS_DIR / "prompt_comparison_results.csv"
RAW_RESPONSES_DIR = RESULTS_DIR / "raw_responses"
RAW_RESPONSES_DIR.mkdir(exist_ok=True)

# ============================================================================
# 3. Prompt模板定义（体现不同的设计理念）
# ============================================================================

# 系统角色定义（所有实验共用）
SYSTEM_PROMPT = """You are an intelligent life assistant specialized in helping international students and workers living in Japan. 
Your task is to analyze conversation history and extract key insights about the user's life situation.
Focus on themes related to study, work, visa issues, social life, health, and travel in Japan."""

# A. 基础Prompt（当前项目使用的简单模式）
BASELINE_TEMPLATE = """
Please analyze the following conversation history and summarize the user's main life aspects.

Conversation History:
{conversation_history}

Please provide a comprehensive summary covering the user's concerns, interests, problems, and plans.
"""

# B. 结构化JSON Prompt（明确指定输出格式）
STRUCTURED_JSON_TEMPLATE = """
Please analyze the following conversation history and extract key information about the user.

Conversation History:
{conversation_history}

You must output ONLY a valid JSON object with exactly these fields:
- "Main_Concerns": string describing the user's primary worries or focus areas
- "Interests": string listing the user's hobbies and interests  
- "Recent_Problems": string describing current challenges or difficulties
- "Action_Plans": string outlining the user's goals and planned actions
- "Emotional_State": string describing the user's general mood and attitude

Output format example:
{{
  "Main_Concerns": "Academic performance and visa renewal",
  "Interests": "Photography, basketball, AI technology",
  "Recent_Problems": "Language barrier in daily communication", 
  "Action_Plans": "Improve Japanese speaking skills, find part-time job",
  "Emotional_State": "Optimistic but sometimes stressed about deadlines"
}}

Output ONLY the JSON object, no additional text or explanation.
"""

# C. 函数调用模式的Schema定义（OpenAI原生结构化输出）
FUNCTION_CALLING_SCHEMA = {
    "name": "extract_user_insights",
    "description": "Extract and structure key insights about the user from conversation history",
    "parameters": {
        "type": "object",
        "properties": {
            "Main_Concerns": {
                "type": "string",
                "description": "User's primary worries, focus areas, or important life aspects"
            },
            "Interests": {
                "type": "string", 
                "description": "User's hobbies, interests, and enjoyable activities"
            },
            "Recent_Problems": {
                "type": "string",
                "description": "Current challenges, difficulties, or obstacles the user is facing"
            },
            "Action_Plans": {
                "type": "string",
                "description": "User's goals, planned actions, and future intentions"
            },
            "Emotional_State": {
                "type": "string",
                "description": "User's general mood, attitude, and emotional well-being"
            }
        },
        "required": REQUIRED_JSON_FIELDS
    }
}

# ============================================================================
# 4. 数据提取和预处理功能
# ============================================================================

def fetch_conversation_history(user_id: int, limit: int) -> str:
    """
    从SQLite数据库提取指定用户的最近对话历史
    
    Args:
        user_id: 用户ID
        limit: 提取的消息条数限制
        
    Returns:
        str: 格式化的对话历史文本
    """
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # 查询最近的对话记录，按时间倒序
            cursor.execute("""
                SELECT role, content, timestamp 
                FROM conversations 
                WHERE user_id = ? 
                ORDER BY id DESC 
                LIMIT ?
            """, (user_id, limit))
            
            conversations = cursor.fetchall()
            
        if not conversations:
            return "No conversation history found for this user."
            
        # 格式化对话历史（时间正序排列）
        formatted_history = []
        for role, content, timestamp in reversed(conversations):
            # 过滤掉系统提示信息
            if not (content.startswith("[User Profile]") or content.startswith("[Memory Summary]")):
                formatted_history.append(f"{role.capitalize()}: {content}")
                
        return "\n\n".join(formatted_history)
        
    except Exception as e:
        print(f"❌ Error fetching conversation history: {e}")
        return ""

def clean_json_response(raw_text: str) -> str:
    """
    清理LLM输出中的多余格式，提取纯JSON内容
    
    Args:
        raw_text: LLM的原始输出文本
        
    Returns:
        str: 清理后的JSON字符串
    """
    text = raw_text.strip()
    
    # 移除markdown代码块标记
    code_block_pattern = r'```(?:json)?\s*(.*?)\s*```'
    match = re.search(code_block_pattern, text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    
    # 处理被引号包围的JSON
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].replace('\\"', '"')
        
    return text

# ============================================================================
# 5. 核心实验执行函数
# ============================================================================

def execute_baseline_prompt(conversation_history: str, temperature: float, top_p: float) -> str:
    """
    执行基础Prompt实验
    
    Args:
        conversation_history: 对话历史文本
        temperature: 随机性控制参数
        top_p: 核采样参数
        
    Returns:
        str: LLM的原始响应文本
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": BASELINE_TEMPLATE.format(conversation_history=conversation_history)}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=800,  # 给予足够空间输出完整内容
    )
    
    return response.choices[0].message.content

def execute_structured_prompt(conversation_history: str, temperature: float, top_p: float) -> str:
    """
    执行结构化JSON Prompt实验
    
    Args:
        conversation_history: 对话历史文本
        temperature: 随机性控制参数
        top_p: 核采样参数
        
    Returns:
        str: LLM的原始响应文本
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": STRUCTURED_JSON_TEMPLATE.format(conversation_history=conversation_history)}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=800,
    )
    
    return response.choices[0].message.content

def execute_function_calling(conversation_history: str, temperature: float, top_p: float) -> str:
    """
    执行函数调用模式实验
    
    Args:
        conversation_history: 对话历史文本
        temperature: 随机性控制参数
        top_p: 核采样参数
        
    Returns:
        str: 函数调用返回的JSON字符串
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze this conversation history:\n\n{conversation_history}"}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[{"type": "function", "function": FUNCTION_CALLING_SCHEMA}],
        tool_choice={"type": "function", "function": {"name": "extract_user_insights"}},
        temperature=temperature,
        top_p=top_p,
        max_tokens=800,
    )
    
    # 提取函数调用的参数（已经是JSON格式）
    tool_call = response.choices[0].message.tool_calls[0]
    return tool_call.function.arguments

# ============================================================================
# 6. 结果评估和指标计算
# ============================================================================

def evaluate_response_quality(raw_response: str) -> dict:
    """
    评估LLM响应的质量指标
    
    Args:
        raw_response: LLM的原始响应
        
    Returns:
        dict: 包含各项评估指标的字典
    """
    metrics = {
        "json_parseable": False,
        "required_fields_present": 0,
        "total_required_fields": len(REQUIRED_JSON_FIELDS),
        "response_length": len(raw_response),
        "empty_fields_count": 0
    }
    
    try:
        # 尝试解析JSON
        cleaned_json = clean_json_response(raw_response)
        parsed_data = json.loads(cleaned_json)
        metrics["json_parseable"] = True
        
        # 检查必需字段的存在性和完整性
        for field in REQUIRED_JSON_FIELDS:
            if field in parsed_data:
                metrics["required_fields_present"] += 1
                # 检查字段是否为空或只包含空白字符
                if not parsed_data[field] or not parsed_data[field].strip():
                    metrics["empty_fields_count"] += 1
                    
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        # JSON解析失败或字段访问错误
        pass
        
    # 计算字段完整率
    metrics["field_completeness_rate"] = metrics["required_fields_present"] / metrics["total_required_fields"]
    
    return metrics

def save_raw_response(response_text: str, experiment_id: str, prompt_type: str, 
                     temperature: float, top_p: float) -> str:
    """
    保存LLM的原始响应到文件
    
    Args:
        response_text: LLM响应文本
        experiment_id: 实验批次ID
        prompt_type: Prompt类型
        temperature: 温度参数
        top_p: top_p参数
        
    Returns:
        str: 保存的文件路径
    """
    filename = f"{experiment_id}_{prompt_type}_temp{temperature}_top_p{top_p}.txt"
    filepath = RAW_RESPONSES_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Experiment: {experiment_id}\n")
        f.write(f"Prompt Type: {prompt_type}\n")
        f.write(f"Temperature: {temperature}\n")
        f.write(f"Top P: {top_p}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write("="*60 + "\n")
        f.write(response_text)
        
    return str(filepath)

# ============================================================================
# 7. 主实验流程控制
# ============================================================================

def run_comprehensive_experiment():
    """
    运行完整的Prompt Engineering对比实验
    """
    print("🚀 Starting Prompt Engineering Experiment")
    print("="*60)
    
    # 生成实验批次ID
    experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"📋 Experiment ID: {experiment_id}")
    
    # 获取实验数据
    print(f"📊 Fetching conversation history for user {TARGET_USER_ID}...")
    conversation_history = fetch_conversation_history(TARGET_USER_ID, N_MESSAGES_TO_FETCH)
    
    if not conversation_history or conversation_history.startswith("No conversation"):
        print("❌ No valid conversation history found. Please check your database.")
        return
        
    print(f"✅ Retrieved {len(conversation_history.split())} words of conversation history")
    
    # 定义实验参数网格
    prompt_types = ["baseline", "structured", "function_calling"]
    temperature_values = [0.0, 0.3, 0.7]  # 低、中、高随机性
    top_p_values = [0.8, 1.0]             # 保守、开放的采样
    
    total_experiments = len(prompt_types) * len(temperature_values) * len(top_p_values)
    print(f"🔬 Running {total_experiments} experiments...")
    
    # 准备结果CSV文件
    csv_headers = [
        "experiment_id", "prompt_type", "temperature", "top_p",
        "json_parseable", "required_fields_present", "total_required_fields",
        "field_completeness_rate", "response_length", "empty_fields_count",
        "raw_file_path", "timestamp"
    ]
    
    # 写入CSV头部（如果文件不存在）
    if not RESULTS_CSV.exists():
        with open(RESULTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(csv_headers)
    
    # 执行实验网格
    experiment_count = 0
    for prompt_type, temperature, top_p in itertools.product(prompt_types, temperature_values, top_p_values):
        experiment_count += 1
        print(f"\n[{experiment_count}/{total_experiments}] Testing: {prompt_type} | temp={temperature} | top_p={top_p}")
        
        try:
            # 根据prompt类型执行相应的实验
            if prompt_type == "baseline":
                response = execute_baseline_prompt(conversation_history, temperature, top_p)
            elif prompt_type == "structured":
                response = execute_structured_prompt(conversation_history, temperature, top_p)
            elif prompt_type == "function_calling":
                response = execute_function_calling(conversation_history, temperature, top_p)
            else:
                raise ValueError(f"Unknown prompt type: {prompt_type}")
            
            # 评估响应质量
            metrics = evaluate_response_quality(response)
            
            # 保存原始响应
            raw_file_path = save_raw_response(response, experiment_id, prompt_type, temperature, top_p)
            
            # 记录结果到CSV
            with open(RESULTS_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    experiment_id, prompt_type, temperature, top_p,
                    metrics["json_parseable"], metrics["required_fields_present"], 
                    metrics["total_required_fields"], metrics["field_completeness_rate"],
                    metrics["response_length"], metrics["empty_fields_count"],
                    raw_file_path, datetime.now().isoformat()
                ])
            
            # 显示实时结果
            status = "✅ PASS" if metrics["json_parseable"] else "❌ FAIL"
            completeness = f"{metrics['required_fields_present']}/{metrics['total_required_fields']}"
            print(f"   Result: {status} | Fields: {completeness} | Length: {metrics['response_length']} chars")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            # 记录错误到CSV
            with open(RESULTS_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    experiment_id, prompt_type, temperature, top_p,
                    False, 0, len(REQUIRED_JSON_FIELDS), 0.0, 0, 0,
                    f"ERROR: {str(e)}", datetime.now().isoformat()
                ])
    
    print("\n" + "="*60)
    print("🎉 Experiment completed successfully!")
    print(f"📁 Results saved to: {RESULTS_CSV}")
    print(f"📄 Raw responses saved to: {RAW_RESPONSES_DIR}")
    print("\n📈 To analyze results, you can:")
    print(f"   • Open {RESULTS_CSV} in Excel or Google Sheets")
    print(f"   • Check individual responses in {RAW_RESPONSES_DIR}")

# ============================================================================
# 8. 脚本入口点
# ============================================================================

if __name__ == "__main__":
    try:
        run_comprehensive_experiment()
    except KeyboardInterrupt:
        print("\n\n⏹️  Experiment interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc() 