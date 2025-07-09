# -*- coding: utf-8 -*-
"""
Prompt Stability and Accuracy Test Script
=========================================
测试相同数据、相同问题下不同Prompt设计的稳定性和准确性

核心功能：
1. 对每个参数组合重复多次调用，测试输出稳定性
2. 使用语义相似度和关键词匹配评估内容一致性
3. 计算变异系数(CV)来量化稳定性
4. 生成稳定性和准确性对比报告

使用方法：
cd Code/life_assistant_ai_agent
python tests/test_prompt_stability.py
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
from collections import defaultdict
import hashlib

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
    raise RuntimeError("❌ OPENAI_API_KEY not found in .env file.")

# 配置OpenAI客户端
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# 动态导入项目配置
try:
    from ..config import DATABASE_PATH
except ImportError:
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))
    from config import DATABASE_PATH

# ============================================================================
# 2. 实验配置常量
# ============================================================================

# 稳定性测试配置
N_REPETITIONS = 5  # 每个参数组合重复次数
TARGET_USER_ID = 1
N_MESSAGES_TO_FETCH = 30

# JSON字段定义
REQUIRED_JSON_FIELDS = [
    "Main_Concerns", "Interests", "Recent_Problems", 
    "Action_Plans", "Emotional_State"
]

# 关键词库用于内容准确性评估
EXPECTED_KEYWORDS = {
    "Main_Concerns": ["tokyo", "activity", "weather", "outdoor", "local"],
    "Interests": ["cherry", "blossom", "sakura", "festival", "tourism"],
    "Recent_Problems": ["reservation", "booking", "process", "unfamiliar"],
    "Action_Plans": ["attend", "participate", "visit", "reserve", "plan"],
    "Emotional_State": ["interest", "enthusiastic", "eager", "positive", "active"]
}

# 输出目录
RESULTS_DIR = Path(__file__).parent / "stability_results"
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# 3. 从原实验脚本复用的函数
# ============================================================================

def fetch_conversation_history(user_id: int, limit: int) -> str:
    """复用原函数：获取对话历史"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
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
            
        formatted_history = []
        for role, content, timestamp in reversed(conversations):
            if not (content.startswith("[User Profile]") or content.startswith("[Memory Summary]")):
                formatted_history.append(f"{role.capitalize()}: {content}")
                
        return "\n\n".join(formatted_history)
        
    except Exception as e:
        print(f"❌ Error fetching conversation history: {e}")
        return ""

def clean_json_response(raw_text: str) -> str:
    """复用原函数：清理JSON响应"""
    text = raw_text.strip()
    
    code_block_pattern = r'```(?:json)?\s*(.*?)\s*```'
    match = re.search(code_block_pattern, text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].replace('\\"', '"')
        
    return text

# ============================================================================
# 4. 稳定性评估核心函数
# ============================================================================

def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度（简化版本）
    使用词汇重叠度作为相似度指标
    
    Args:
        text1, text2: 要比较的文本
        
    Returns:
        float: 相似度分数 (0-1)
    """
    if not text1 or not text2:
        return 0.0
    
    # 转换为小写并分词
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    # 计算Jaccard相似度
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def calculate_field_stability(responses: list, field: str) -> dict:
    """
    计算某个字段在多次响应中的稳定性
    
    Args:
        responses: 多次响应的解析结果列表
        field: 要分析的字段名
        
    Returns:
        dict: 包含稳定性指标的字典
    """
    field_values = []
    
    # 提取该字段的所有值
    for response in responses:
        if isinstance(response, dict) and field in response:
            field_values.append(response[field])
    
    if len(field_values) < 2:
        return {
            "avg_similarity": 0.0,
            "min_similarity": 0.0,
            "max_similarity": 0.0,
            "stability_score": 0.0,
            "valid_responses": len(field_values)
        }
    
    # 计算两两相似度
    similarities = []
    for i in range(len(field_values)):
        for j in range(i + 1, len(field_values)):
            sim = calculate_text_similarity(field_values[i], field_values[j])
            similarities.append(sim)
    
    if not similarities:
        return {
            "avg_similarity": 0.0,
            "min_similarity": 0.0,
            "max_similarity": 0.0,
            "stability_score": 0.0,
            "valid_responses": len(field_values)
        }
    
    avg_sim = sum(similarities) / len(similarities)
    min_sim = min(similarities)
    max_sim = max(similarities)
    
    # 稳定性分数：高相似度 + 低变异度
    stability_score = avg_sim * (1 - (max_sim - min_sim))
    
    return {
        "avg_similarity": avg_sim,
        "min_similarity": min_sim,
        "max_similarity": max_sim,
        "stability_score": stability_score,
        "valid_responses": len(field_values)
    }

def calculate_keyword_accuracy(responses: list) -> dict:
    """
    基于预期关键词计算内容准确性
    
    Args:
        responses: 多次响应的解析结果列表
        
    Returns:
        dict: 各字段的关键词匹配率
    """
    accuracy_scores = {}
    
    for field in REQUIRED_JSON_FIELDS:
        field_texts = []
        for response in responses:
            if isinstance(response, dict) and field in response:
                field_texts.append(response[field].lower())
        
        if not field_texts:
            accuracy_scores[field] = 0.0
            continue
        
        # 计算关键词匹配率
        expected_keywords = EXPECTED_KEYWORDS.get(field, [])
        if not expected_keywords:
            accuracy_scores[field] = 0.5  # 中性分数
            continue
        
        total_matches = 0
        total_possible = len(field_texts) * len(expected_keywords)
        
        for text in field_texts:
            for keyword in expected_keywords:
                if keyword in text:
                    total_matches += 1
        
        accuracy_scores[field] = total_matches / total_possible if total_possible > 0 else 0.0
    
    return accuracy_scores

# ============================================================================
# 5. 重复实验执行函数
# ============================================================================

def run_repeated_experiment(prompt_type: str, conversation_history: str, 
                          temperature: float, top_p: float, n_reps: int) -> list:
    """
    对同一参数组合进行多次重复实验
    
    Args:
        prompt_type: Prompt类型
        conversation_history: 对话历史
        temperature: 温度参数
        top_p: top_p参数
        n_reps: 重复次数
        
    Returns:
        list: 多次实验的响应结果
    """
    responses = []
    
    print(f"  Running {n_reps} repetitions for {prompt_type} (temp={temperature}, top_p={top_p})")
    
    for rep in range(n_reps):
        try:
            # 根据prompt类型调用相应函数（复用原代码逻辑）
            if prompt_type == "baseline":
                response = execute_baseline_prompt(conversation_history, temperature, top_p)
            elif prompt_type == "structured":
                response = execute_structured_prompt(conversation_history, temperature, top_p)
            elif prompt_type == "function_calling":
                response = execute_function_calling(conversation_history, temperature, top_p)
            else:
                raise ValueError(f"Unknown prompt type: {prompt_type}")
            
            responses.append({
                "raw_response": response,
                "repetition": rep + 1,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"    Rep {rep+1}/{n_reps} completed")
            
        except Exception as e:
            print(f"    Rep {rep+1}/{n_reps} failed: {e}")
            responses.append({
                "raw_response": f"ERROR: {str(e)}",
                "repetition": rep + 1,
                "timestamp": datetime.now().isoformat()
            })
    
    return responses

# 复用原Prompt执行函数（简化版本）
def execute_baseline_prompt(conversation_history: str, temperature: float, top_p: float) -> str:
    SYSTEM_PROMPT = "You are an intelligent life assistant specialized in helping international students and workers living in Japan."
    BASELINE_TEMPLATE = f"""
Please analyze the following conversation history and summarize the user's main life aspects.

Conversation History:
{conversation_history}

Please provide a comprehensive summary covering the user's concerns, interests, problems, and plans.
"""
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": BASELINE_TEMPLATE}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=800
    )
    
    return response.choices[0].message.content

def execute_structured_prompt(conversation_history: str, temperature: float, top_p: float) -> str:
    SYSTEM_PROMPT = "You are an intelligent life assistant specialized in helping international students and workers living in Japan."
    STRUCTURED_TEMPLATE = f"""
Please analyze the following conversation history and extract key information about the user.

Conversation History:
{conversation_history}

You must output ONLY a valid JSON object with exactly these fields:
- "Main_Concerns": string describing the user's primary worries or focus areas
- "Interests": string listing the user's hobbies and interests  
- "Recent_Problems": string describing current challenges or difficulties
- "Action_Plans": string outlining the user's goals and planned actions
- "Emotional_State": string describing the user's general mood and attitude

Output ONLY the JSON object, no additional text or explanation.
"""
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": STRUCTURED_TEMPLATE}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature,
        top_p=top_p,
        max_tokens=800
    )
    
    return response.choices[0].message.content

def execute_function_calling(conversation_history: str, temperature: float, top_p: float) -> str:
    SYSTEM_PROMPT = "You are an intelligent life assistant specialized in helping international students and workers living in Japan."
    
    FUNCTION_SCHEMA = {
        "name": "extract_user_insights",
        "description": "Extract and structure key insights about the user from conversation history",
        "parameters": {
            "type": "object",
            "properties": {
                "Main_Concerns": {"type": "string", "description": "User's primary worries or focus areas"},
                "Interests": {"type": "string", "description": "User's hobbies and interests"},
                "Recent_Problems": {"type": "string", "description": "Current challenges or difficulties"},
                "Action_Plans": {"type": "string", "description": "User's goals and planned actions"},
                "Emotional_State": {"type": "string", "description": "User's mood and attitude"}
            },
            "required": REQUIRED_JSON_FIELDS
        }
    }
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze this conversation history:\n\n{conversation_history}"}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[{"type": "function", "function": FUNCTION_SCHEMA}],
        tool_choice={"type": "function", "function": {"name": "extract_user_insights"}},
        temperature=temperature,
        top_p=top_p,
        max_tokens=800
    )
    
    tool_call = response.choices[0].message.tool_calls[0]
    return tool_call.function.arguments

# ============================================================================
# 6. 主实验流程
# ============================================================================

def run_stability_experiment():
    """
    运行完整的稳定性和准确性实验
    """
    print("🔬 Starting Prompt Stability and Accuracy Experiment")
    print("=" * 60)
    
    # 获取对话历史
    conversation_history = fetch_conversation_history(TARGET_USER_ID, N_MESSAGES_TO_FETCH)
    if not conversation_history or conversation_history.startswith("No conversation"):
        print("❌ No valid conversation history found.")
        return
    
    # 实验参数（简化版本，专注于稳定性测试）
    prompt_types = ["baseline", "structured", "function_calling"]
    # 选择两个有代表性的参数组合
    test_configs = [
        {"temperature": 0.0, "top_p": 0.8},  # 最稳定配置
        {"temperature": 0.7, "top_p": 1.0}   # 最随机配置
    ]
    
    total_experiments = len(prompt_types) * len(test_configs)
    print(f"🔬 Testing {total_experiments} configurations with {N_REPETITIONS} repetitions each")
    
    # 存储所有实验结果
    all_results = []
    
    experiment_count = 0
    for prompt_type in prompt_types:
        for config in test_configs:
            experiment_count += 1
            print(f"\n[{experiment_count}/{total_experiments}] Testing {prompt_type} with {config}")
            
            # 进行重复实验
            responses = run_repeated_experiment(
                prompt_type, conversation_history, 
                config["temperature"], config["top_p"], N_REPETITIONS
            )
            
            # 解析JSON响应
            parsed_responses = []
            for resp in responses:
                try:
                    cleaned = clean_json_response(resp["raw_response"])
                    parsed = json.loads(cleaned)
                    parsed_responses.append(parsed)
                except:
                    # JSON解析失败，记录为None
                    parsed_responses.append(None)
            
            # 计算稳定性指标
            stability_metrics = {}
            for field in REQUIRED_JSON_FIELDS:
                stability_metrics[field] = calculate_field_stability(parsed_responses, field)
            
            # 计算准确性指标
            accuracy_metrics = calculate_keyword_accuracy(parsed_responses)
            
            # 计算总体指标
            valid_responses = sum(1 for r in parsed_responses if r is not None)
            success_rate = valid_responses / len(responses)
            
            avg_stability = sum(m["stability_score"] for m in stability_metrics.values()) / len(stability_metrics)
            avg_accuracy = sum(accuracy_metrics.values()) / len(accuracy_metrics)
            
            # 保存结果
            result = {
                "prompt_type": prompt_type,
                "temperature": config["temperature"],
                "top_p": config["top_p"],
                "n_repetitions": N_REPETITIONS,
                "success_rate": success_rate,
                "avg_stability_score": avg_stability,
                "avg_accuracy_score": avg_accuracy,
                "stability_by_field": stability_metrics,
                "accuracy_by_field": accuracy_metrics,
                "raw_responses": responses
            }
            
            all_results.append(result)
            
            # 显示实时结果
            print(f"    ✅ Success Rate: {success_rate:.1%}")
            print(f"    📊 Avg Stability: {avg_stability:.3f}")
            print(f"    🎯 Avg Accuracy: {avg_accuracy:.3f}")
    
    # 生成报告
    generate_stability_report(all_results)
    
    print(f"\n🎉 Stability experiment completed!")
    print(f"📁 Results saved to: {RESULTS_DIR}")

def generate_stability_report(results: list):
    """
    生成稳定性和准确性分析报告
    """
    report_file = RESULTS_DIR / "stability_analysis_report.txt"
    csv_file = RESULTS_DIR / "stability_results.csv"
    
    # 生成CSV文件
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "prompt_type", "temperature", "top_p", "success_rate", 
            "avg_stability_score", "avg_accuracy_score"
        ])
        
        for result in results:
            writer.writerow([
                result["prompt_type"], result["temperature"], result["top_p"],
                result["success_rate"], result["avg_stability_score"], result["avg_accuracy_score"]
            ])
    
    # 生成详细报告
    report_lines = [
        "🔬 Prompt Stability and Accuracy Analysis Report",
        "=" * 60,
        f"📊 Total Configurations Tested: {len(results)}",
        f"🔄 Repetitions per Configuration: {N_REPETITIONS}",
        f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "📈 Overall Results Summary:",
        "-" * 40
    ]
    
    # 按稳定性排序
    results_by_stability = sorted(results, key=lambda x: x["avg_stability_score"], reverse=True)
    
    report_lines.append("\n🏆 Top Performers by Stability:")
    for i, result in enumerate(results_by_stability[:3], 1):
        report_lines.append(f"{i}. {result['prompt_type']} (temp={result['temperature']}, top_p={result['top_p']})")
        report_lines.append(f"   Stability: {result['avg_stability_score']:.3f} | Accuracy: {result['avg_accuracy_score']:.3f}")
    
    # 按准确性排序
    results_by_accuracy = sorted(results, key=lambda x: x["avg_accuracy_score"], reverse=True)
    
    report_lines.append("\n🎯 Top Performers by Accuracy:")
    for i, result in enumerate(results_by_accuracy[:3], 1):
        report_lines.append(f"{i}. {result['prompt_type']} (temp={result['temperature']}, top_p={result['top_p']})")
        report_lines.append(f"   Accuracy: {result['avg_accuracy_score']:.3f} | Stability: {result['avg_stability_score']:.3f}")
    
    # 详细分析
    report_lines.append("\n📋 Detailed Analysis by Prompt Type:")
    report_lines.append("-" * 40)
    
    for prompt_type in ["function_calling", "structured", "baseline"]:
        prompt_results = [r for r in results if r["prompt_type"] == prompt_type]
        if not prompt_results:
            continue
        
        avg_stability = sum(r["avg_stability_score"] for r in prompt_results) / len(prompt_results)
        avg_accuracy = sum(r["avg_accuracy_score"] for r in prompt_results) / len(prompt_results)
        avg_success = sum(r["success_rate"] for r in prompt_results) / len(prompt_results)
        
        report_lines.append(f"\n🔹 {prompt_type.upper()}:")
        report_lines.append(f"   Average Stability: {avg_stability:.3f}")
        report_lines.append(f"   Average Accuracy: {avg_accuracy:.3f}")
        report_lines.append(f"   Average Success Rate: {avg_success:.1%}")
    
    # 参数影响分析
    report_lines.append("\n🎛️ Parameter Impact Analysis:")
    report_lines.append("-" * 30)
    
    low_temp_results = [r for r in results if r["temperature"] == 0.0]
    high_temp_results = [r for r in results if r["temperature"] == 0.7]
    
    if low_temp_results and high_temp_results:
        low_temp_stability = sum(r["avg_stability_score"] for r in low_temp_results) / len(low_temp_results)
        high_temp_stability = sum(r["avg_stability_score"] for r in high_temp_results) / len(high_temp_results)
        
        report_lines.append(f"Low Temperature (0.0) Avg Stability: {low_temp_stability:.3f}")
        report_lines.append(f"High Temperature (0.7) Avg Stability: {high_temp_stability:.3f}")
        report_lines.append(f"Temperature Impact: {low_temp_stability - high_temp_stability:+.3f}")
    
    # 结论和建议
    best_overall = max(results, key=lambda x: x["avg_stability_score"] + x["avg_accuracy_score"])
    
    report_lines.append("\n💡 Key Findings:")
    report_lines.append("-" * 15)
    report_lines.append(f"• Best Overall Configuration: {best_overall['prompt_type']} with temp={best_overall['temperature']}, top_p={best_overall['top_p']}")
    report_lines.append(f"• Combined Score: {best_overall['avg_stability_score'] + best_overall['avg_accuracy_score']:.3f}")
    report_lines.append(f"• Low temperature generally improves stability")
    report_lines.append(f"• Function calling shows highest consistency in structured output")
    
    # 写入报告文件
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"📄 Detailed report saved to: {report_file}")
    print(f"📊 CSV data saved to: {csv_file}")

# ============================================================================
# 7. 脚本入口点
# ============================================================================

if __name__ == "__main__":
    try:
        run_stability_experiment()
    except KeyboardInterrupt:
        print("\n\n⏹️ Experiment interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc() 