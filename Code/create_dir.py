# 创建项目的初始目录结构
import os

# 定义初始项目结构
project_root = "/Users/dz_xl/Library/Mobile Documents/com~apple~CloudDocs/2025霓虹/Waseda_University/Ai_Agent/Code/life_assistant_ai_agent"
dirs_to_create = [
    "agents",
    "data",
    "memory",
    "utils",
    "assets"
]

# 创建主目录和子目录
os.makedirs(project_root, exist_ok=True)
for dir_name in dirs_to_create:
    os.makedirs(os.path.join(project_root, dir_name), exist_ok=True)

# 创建一些空的初始文件
initial_files = {
    "app.py": "# Main entry point for Streamlit App\n",
    ".env": "# Add your OpenAI API Key like this:\n# OPENAI_API_KEY=your_key_here\n",
    "README.md": "# AI Agent Life Assistant Web App\n",
    "utils/prompts.py": "# Store all prompt templates here\n",
    "agents/reminder.py": "# Reminder agent functions\n",
    "agents/memory_agent.py": "# Memory agent functions\n",
    "agents/context_agent.py": "# Context-aware life assistant functions\n",
    "memory/user_memory.yaml": "# This file stores user memory in YAML format\n",
    "data/reminders.db": ""  # SQLite 文件会在运行时创建结构
}

# 写入初始文件内容
for filename, content in initial_files.items():
    file_path = os.path.join(project_root, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

