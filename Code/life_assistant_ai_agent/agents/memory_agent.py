# Memory agent functions
"""
LLM问答+记忆体：负责智能问答、个性化记忆管理与调用。
"""
import sqlite3
import yaml
import os
import signal
from datetime import datetime
from utils.openai_api import call_openai
from config import DATABASE_PATH
from pathlib import Path

class MemoryAgent:
    def __init__(self, user_id, page_size=5):
        self.user_id = user_id
        self.page_size = page_size
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
        self.messages = []
        self.group_id = self._get_latest_group_id() + 1
        self._load_user_profile()
        self._init_messages(is_new=True)
        self._register_signal()
        self._dirty = False
        self._saved_message_count = 0

    def _get_latest_group_id(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(group_id) FROM conversations WHERE user_id=?", (self.user_id,))
        result = cursor.fetchone()
        return result[0] if result and result[0] else 0

    def _load_user_profile(self):
        # 读取yaml缓存，加载用户画像和记忆摘要
        memory_path = Path(__file__).parent.parent / "memory" / "user_memory.yaml"
        self.user_profile = ""
        self.memory_summary = ""
        if memory_path.exists():
            with open(memory_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            for u in data.get("users", []):
                if u["user_profile"]["user_id"] == self.user_id:
                    self.user_profile = self._profile_to_str(u["user_profile"])
                    if u.get("memory_summaries"):
                        self.memory_summary = u["memory_summaries"][-1]["summary"]
                    break

    def _profile_to_str(self, profile):
        return f"姓名：{profile.get('name','')}，年龄：{profile.get('age','')}，性别：{profile.get('gender','')}，学历：{profile.get('education','')}，职业：{profile.get('occupation','')}，兴趣：{','.join(profile.get('interests',[]))}，语言：{','.join(profile.get('language',[]))}，国籍：{profile.get('nationality','')}"

    def _init_messages(self, is_new=True):
        self.messages = []
        if is_new:
            self.messages.append({"role": "system", "content": "你是一个生活助理，善于总结和建议。"})
            if self.user_profile:
                self.messages.append({"role": "user", "content": f"[用户画像] {self.user_profile}"})
            if self.memory_summary:
                self.messages.append({"role": "user", "content": f"[记忆摘要] {self.memory_summary}"})

    def _register_signal(self):
        def handler(sig, frame):
            print("\n检测到退出信号，正在保存当前对话...")
            self.save()
            print("保存完成，安全退出。")
            exit(0)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def ask(self, question):
        self.messages.append({"role": "user", "content": question})
        answer = call_openai(self.messages)
        self.messages.append({"role": "assistant", "content": answer})
        self._dirty = True
        return answer

    def save(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        for msg in self.messages[self._saved_message_count:]:
            if msg["role"] in ("user", "assistant") and not (isinstance(msg["content"], str) and (msg["content"].startswith("[用户画像]") or msg["content"].startswith("[记忆摘要]"))):
                cursor.execute(
                    "INSERT INTO conversations (user_id, group_id, role, content, timestamp, tags) VALUES (?, ?, ?, ?, ?, ?) ",
                    (self.user_id, self.group_id, msg["role"], msg["content"], now, "")
                )
        self.conn.commit()
        self._saved_message_count = len(self.messages)
        self._update_yaml_cache()
        self._dirty = False

    def _update_yaml_cache(self):
        memory_path = Path(__file__).parent.parent / "memory" / "user_memory.yaml"
        if not memory_path.exists():
            return
        with open(memory_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for u in data.get("users", []):
            if u["user_profile"]["user_id"] == self.user_id:
                # 只缓存最近一组对话
                u["conversations"] = [{
                    "group_id": self.group_id,
                    "messages": [m for m in self.messages if m["role"] in ("user", "assistant")]
                }]
        with open(memory_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True)

    def new_conversation(self):
        if self._dirty:
            self.save()
        self.group_id = self._get_latest_group_id() + 1
        self._init_messages(is_new=True)
        self._saved_message_count = 0

    def show_history(self, page=1):
        msgs = [m for m in self.messages if m["role"] in ("user", "assistant") and not (isinstance(m["content"], str) and (m["content"].startswith("[用户画像]") or m["content"].startswith("[记忆摘要]")))]
        total = len(msgs)
        start = (page-1)*self.page_size
        end = min(start+self.page_size, total)
        for idx, m in enumerate(msgs[start:end], start=start+1):
            print(f"[{idx}] {m['role']}: {m['content']}")
        print(f"-- 第{page}页，共{(total-1)//self.page_size+1}页 --")

    def switch_conversation(self, group_id):
        if self._dirty:
            self.save()
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content FROM conversations WHERE user_id=? AND group_id=? ORDER BY id ASC",
            (self.user_id, group_id)
        )
        rows = cursor.fetchall()
        self.group_id = group_id
        self._init_messages(is_new=False)
        for r in rows:
            self.messages.append({"role": r["role"], "content": r["content"]})
        self._saved_message_count = len(self.messages)

    def list_conversations(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT DISTINCT group_id FROM conversations WHERE user_id=? ORDER BY group_id ASC",
            (self.user_id,)
        )
        return [row[0] for row in cursor.fetchall()]

    def record_interaction(self, question, answer):
        """记录用户问答内容摘要"""
        pass
    def update_user_profile(self, info):
        """更新用户画像信息"""
        pass
    def personalized_reply(self, question):
        """结合记忆体生成个性化回答"""
        pass