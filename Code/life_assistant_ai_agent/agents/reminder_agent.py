# Reminder agent functions
"""
AI提醒助手：负责任务的记录、分类、优先级分析与提醒策略。
"""
import sqlite3
from config import DATABASE_PATH
from utils.openai_api import call_openai

class ReminderAgent:
    def __init__(self, user_id):
        self.user_id = user_id
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row

    def fetch_reminders(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT title, description, due_date, priority, status FROM reminders WHERE user_id=? AND status='待办' ORDER BY due_date ASC",
            (self.user_id,)
        )
        reminders = cursor.fetchall()
        return reminders

    def generate_prompt(self, reminders):
        if not reminders:
            return "用户暂无待办事项。"
        items = []
        for r in reminders:
            items.append(f"- {r['title']}（{r['due_date']}，优先级：{r['priority']}）：{r['description']}")
        reminders_text = "\n".join(items)
        prompt = f"""
你是一个生活助理，请根据以下日程和待办事项，帮我总结出今天/本周最重要的事项，并按优先级排序，给出简明的提醒建议。输出中英双语版本。
日程和待办事项如下：
{reminders_text}
请输出格式：
中文版本：
1. 事项A（优先级：高）- 简要说明
2. 事项B（优先级：中）- 简要说明
English Version：
1. Task A (Priority: High) - Brief description
2. Task B (Priority: Medium) - Brief description
"""
        return prompt

    def get_smart_reminders(self):
        reminders = self.fetch_reminders()
        prompt = self.generate_prompt(reminders)
        if prompt == "用户暂无待办事项。":
            return prompt
        result = call_openai(prompt)
        return result

    def add_task(self, task):
        """添加新任务"""
        pass
    def analyze_tasks(self):
        """分析任务优先级与提醒时机"""
        pass
    def get_reminders(self):
        """生成今日/近期提醒"""
        pass