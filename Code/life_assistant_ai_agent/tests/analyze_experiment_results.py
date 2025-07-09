# -*- coding: utf-8 -*-
"""
Prompt Experiment Results Analysis Script
========================================
分析Prompt Engineering实验结果，生成可视化图表和统计报告

功能：
1. 读取实验结果CSV文件
2. 计算各种Prompt设计的成功率统计
3. 生成对比图表（如果安装了matplotlib）
4. 输出详细的分析报告

使用方法：
python tests/analyze_experiment_results.py
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

def load_experiment_results(csv_path: Path) -> list:
    """
    加载实验结果CSV文件
    
    Args:
        csv_path: CSV文件路径
        
    Returns:
        list: 实验结果数据列表
    """
    if not csv_path.exists():
        print(f"❌ Results file not found: {csv_path}")
        return []
    
    results = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 转换数值字段
            row['temperature'] = float(row['temperature'])
            row['top_p'] = float(row['top_p'])
            row['json_parseable'] = row['json_parseable'] == 'True'
            row['required_fields_present'] = int(row['required_fields_present'])
            row['field_completeness_rate'] = float(row['field_completeness_rate'])
            row['response_length'] = int(row['response_length'])
            row['empty_fields_count'] = int(row['empty_fields_count'])
            results.append(row)
    
    return results

def analyze_by_prompt_type(results: list) -> dict:
    """
    按Prompt类型分析结果
    
    Args:
        results: 实验结果列表
        
    Returns:
        dict: 按prompt类型汇总的统计数据
    """
    stats = defaultdict(lambda: {
        'total_runs': 0,
        'successful_parses': 0,
        'avg_completeness': 0.0,
        'avg_response_length': 0.0,
        'parse_success_rate': 0.0
    })
    
    for result in results:
        prompt_type = result['prompt_type']
        stats[prompt_type]['total_runs'] += 1
        
        if result['json_parseable']:
            stats[prompt_type]['successful_parses'] += 1
        
        stats[prompt_type]['avg_completeness'] += result['field_completeness_rate']
        stats[prompt_type]['avg_response_length'] += result['response_length']
    
    # 计算平均值
    for prompt_type in stats:
        total = stats[prompt_type]['total_runs']
        if total > 0:
            stats[prompt_type]['parse_success_rate'] = stats[prompt_type]['successful_parses'] / total
            stats[prompt_type]['avg_completeness'] /= total
            stats[prompt_type]['avg_response_length'] /= total
    
    return dict(stats)

def analyze_by_parameters(results: list) -> dict:
    """
    按API参数分析结果
    
    Args:
        results: 实验结果列表
        
    Returns:
        dict: 按参数组合汇总的统计数据
    """
    param_stats = defaultdict(lambda: {
        'total_runs': 0,
        'successful_parses': 0,
        'avg_completeness': 0.0
    })
    
    for result in results:
        key = f"temp_{result['temperature']}_top_p_{result['top_p']}"
        param_stats[key]['total_runs'] += 1
        
        if result['json_parseable']:
            param_stats[key]['successful_parses'] += 1
        
        param_stats[key]['avg_completeness'] += result['field_completeness_rate']
    
    # 计算平均值和成功率
    for key in param_stats:
        total = param_stats[key]['total_runs']
        if total > 0:
            param_stats[key]['parse_success_rate'] = param_stats[key]['successful_parses'] / total
            param_stats[key]['avg_completeness'] /= total
    
    return dict(param_stats)

def generate_report(results: list) -> str:
    """
    生成详细的分析报告
    
    Args:
        results: 实验结果列表
        
    Returns:
        str: 格式化的报告文本
    """
    if not results:
        return "❌ No experiment data available for analysis."
    
    prompt_stats = analyze_by_prompt_type(results)
    param_stats = analyze_by_parameters(results)
    
    report = []
    report.append("🔬 Prompt Engineering Experiment Analysis Report")
    report.append("=" * 60)
    report.append(f"📊 Total experiments conducted: {len(results)}")
    
    # 按Prompt类型的分析
    report.append("\n📋 Analysis by Prompt Type:")
    report.append("-" * 40)
    
    for prompt_type, stats in prompt_stats.items():
        report.append(f"\n🔹 {prompt_type.upper()}:")
        report.append(f"   • Success Rate: {stats['parse_success_rate']:.1%}")
        report.append(f"   • Avg Completeness: {stats['avg_completeness']:.1%}")
        report.append(f"   • Avg Response Length: {stats['avg_response_length']:.0f} chars")
        report.append(f"   • Total Runs: {stats['total_runs']}")
    
    # 最佳Prompt类型
    best_prompt = max(prompt_stats.keys(), 
                     key=lambda x: prompt_stats[x]['parse_success_rate'])
    report.append(f"\n🏆 Best Performing Prompt: {best_prompt}")
    report.append(f"   Success Rate: {prompt_stats[best_prompt]['parse_success_rate']:.1%}")
    
    # 按参数的分析
    report.append(f"\n🎛️  Analysis by API Parameters:")
    report.append("-" * 40)
    
    for param_combo, stats in sorted(param_stats.items()):
        report.append(f"\n🔹 {param_combo}:")
        report.append(f"   • Success Rate: {stats['parse_success_rate']:.1%}")
        report.append(f"   • Avg Completeness: {stats['avg_completeness']:.1%}")
    
    # 最佳参数组合
    best_params = max(param_stats.keys(), 
                     key=lambda x: param_stats[x]['parse_success_rate'])
    report.append(f"\n🏆 Best Parameter Combination: {best_params}")
    report.append(f"   Success Rate: {param_stats[best_params]['parse_success_rate']:.1%}")
    
    # 总结和建议
    report.append(f"\n💡 Key Insights:")
    report.append("-" * 20)
    
    # 计算总体成功率
    total_success = sum(1 for r in results if r['json_parseable'])
    overall_success_rate = total_success / len(results)
    report.append(f"• Overall JSON parsing success rate: {overall_success_rate:.1%}")
    
    # Prompt类型对比
    prompt_success_rates = {pt: stats['parse_success_rate'] 
                           for pt, stats in prompt_stats.items()}
    sorted_prompts = sorted(prompt_success_rates.items(), 
                           key=lambda x: x[1], reverse=True)
    
    report.append(f"• Prompt effectiveness ranking:")
    for i, (prompt_type, rate) in enumerate(sorted_prompts, 1):
        report.append(f"  {i}. {prompt_type}: {rate:.1%}")
    
    # 参数影响分析
    temp_analysis = defaultdict(list)
    for result in results:
        temp_analysis[result['temperature']].append(result['json_parseable'])
    
    report.append(f"\n• Temperature impact:")
    for temp in sorted(temp_analysis.keys()):
        success_rate = sum(temp_analysis[temp]) / len(temp_analysis[temp])
        report.append(f"  temp={temp}: {success_rate:.1%} success rate")
    
    return "\n".join(report)

def save_analysis_report(report: str, output_path: Path):
    """
    保存分析报告到文件
    
    Args:
        report: 报告文本
        output_path: 输出文件路径
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📄 Analysis report saved to: {output_path}")

def main():
    """
    主分析流程
    """
    print("📈 Starting experiment results analysis...")
    
    # 定位结果文件
    results_dir = Path(__file__).parent / "experiment_results"
    csv_file = results_dir / "prompt_comparison_results.csv"
    
    if not csv_file.exists():
        print(f"❌ No experiment results found at: {csv_file}")
        print("💡 Please run the experiment first: python tests/test_prompt_experiments.py")
        return
    
    # 加载和分析数据
    results = load_experiment_results(csv_file)
    if not results:
        return
    
    print(f"✅ Loaded {len(results)} experiment records")
    
    # 生成分析报告
    report = generate_report(results)
    print("\n" + report)
    
    # 保存报告
    report_file = results_dir / "analysis_report.txt"
    save_analysis_report(report, report_file)
    
    # 尝试生成可视化图表（可选）
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        
        # 转换为DataFrame便于可视化
        df = pd.DataFrame(results)
        
        # 创建成功率对比图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Prompt类型成功率对比
        prompt_success = df.groupby('prompt_type')['json_parseable'].mean()
        prompt_success.plot(kind='bar', ax=ax1, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax1.set_title('JSON Parsing Success Rate by Prompt Type')
        ax1.set_ylabel('Success Rate')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. 温度参数影响
        temp_success = df.groupby('temperature')['json_parseable'].mean()
        temp_success.plot(kind='line', marker='o', ax=ax2, color='#FF6B6B')
        ax2.set_title('Success Rate vs Temperature')
        ax2.set_xlabel('Temperature')
        ax2.set_ylabel('Success Rate')
        
        # 3. 字段完整性对比
        completeness = df.groupby('prompt_type')['field_completeness_rate'].mean()
        completeness.plot(kind='bar', ax=ax3, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        ax3.set_title('Field Completeness Rate by Prompt Type')
        ax3.set_ylabel('Completeness Rate')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. 响应长度分布
        df.boxplot(column='response_length', by='prompt_type', ax=ax4)
        ax4.set_title('Response Length Distribution by Prompt Type')
        ax4.set_ylabel('Response Length (chars)')
        
        plt.tight_layout()
        
        # 保存图表
        chart_file = results_dir / "analysis_charts.png"
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        print(f"📊 Visualization charts saved to: {chart_file}")
        
    except ImportError:
        print("📊 Matplotlib not available - skipping visualization")
        print("💡 Install with: pip install matplotlib pandas")

if __name__ == "__main__":
    main() 