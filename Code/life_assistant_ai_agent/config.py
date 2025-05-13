"""
全局配置文件：API Key、数据库路径等。
"""
import os

# 获取当前config.py文件的目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "reminders.db")

# # 优先从环境变量读取 API Key
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")