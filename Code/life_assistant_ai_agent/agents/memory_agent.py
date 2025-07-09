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
from utils.user_profile_utils import parse_user_profile_from_llm, parse_memory_summary_from_llm
import json

class MemoryAgent:
    def __init__(self, user_id, page_size=5):
        self.user_id = user_id
        self.page_size = page_size
        # 不再持久化数据库连接，避免跨线程使用导致的sqlite3.ProgrammingError
        # self.conn = sqlite3.connect(DATABASE_PATH)
        self.messages = []
        self.group_id = self._get_latest_group_id()
        self._load_user_profile()
        self._dirty = False # 提前初始化
        # ===== 逻辑说明 =====
        # 如果该用户有历史对话组（group_id > 0），则自动载入最新 group_id 的历史消息，
        # 这样 show_history 能正常显示历史内容，用户无需手动 /switch。
        # 否则（新用户或无历史对话组），初始化新对话上下文。
        if self.group_id > 0:
            self.switch_conversation(self.group_id)
        else:
            self._init_messages(is_new=True)
        # 只在主线程注册 signal，防止在 Streamlit/Web 环境下报错
        import threading
        if threading.current_thread() is threading.main_thread():
            # 只有命令行/主线程环境下才注册 signal，Web/Streamlit 环境下会跳过
            self._register_signal()
        self._saved_message_count = 0

    def _get_latest_group_id(self):
        # 每次调用都新建数据库连接，避免跨线程sqlite对象报错
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
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
        return f"Name: {profile.get('name','')}, Age: {profile.get('age','')}, Gender: {profile.get('gender','')}, Education: {profile.get('education','')}, Occupation: {profile.get('occupation','')}, Interests: {','.join(profile.get('interests',[]))}, Language: {','.join(profile.get('language',[]))}, Nationality: {profile.get('nationality','')}"

    def _init_messages(self, is_new=True):
        self.messages = []
        if is_new:
            self.messages.append({"role": "system", "content": "You are a life assistant, good at summarizing and giving advice."})
            if self.user_profile:
                self.messages.append({"role": "user", "content": f"[User Profile] {self.user_profile}"})
            if self.memory_summary:
                self.messages.append({"role": "user", "content": f"[Memory Summary] {self.memory_summary}"})

    def _register_signal(self):
        def handler(sig, frame):
            print("\nExit signal detected, saving current conversation...")
            self.save()
            print("Save complete. Exiting safely.")
            exit(0)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def ask(self, user_input):
        # 处理用户输入，生成AI回复，并保存到历史
        self.messages.append({"role": "user", "content": user_input})
        # 这里省略调用大模型的部分，假设直接返回一个简单回复
        ai_reply = f"Echo: {user_input}"
        self.messages.append({"role": "assistant", "content": ai_reply})
        self._dirty = True
        self.save()
        return ai_reply

    def save(self):
        # 保存对话历史到数据库，每次调用都新建连接，避免跨线程sqlite对象报错
        if not self._dirty:
            return
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            for msg in self.messages[self._saved_message_count:]:
                cursor.execute(
                    "INSERT INTO conversations (user_id, group_id, role, content, timestamp, tags) VALUES (?, ?, ?, ?, datetime('now', 'localtime'), ?)",
                    (self.user_id, self.group_id, msg["role"], msg["content"], "")
                )
            conn.commit()
            self._saved_message_count = len(self.messages)
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
        """
        开启新对话组，group_id 自增
        """
        # 新建对话组时也要新建数据库连接，避免跨线程sqlite对象报错
        self.group_id = self._get_latest_group_id() + 1
        self._init_messages(is_new=True)
        self._saved_message_count = 0

    def show_history(self, page=1):
        """
        分页显示对话历史，当前为正序分页（旧→新）。如需倒序分页，将下方注释取消。
        :param page: 页码，从1开始
        """
        msgs = [m for m in self.messages if m["role"] in ("user", "assistant") and not (isinstance(m["content"], str) and (m["content"].startswith("[User Profile]") or m["content"].startswith("[Memory Summary]")))]
        # msgs = list(reversed(msgs))  # 如需倒序分页（新→旧），取消本行注释
        total = len(msgs)
        start = (page-1)*self.page_size
        end = min(start+self.page_size, total)
        for idx, m in enumerate(msgs[start:end], start=start+1):
            print(f"[{idx}] {m['role']}: {m['content']}")
        print(f"-- Page {page} of {(total-1)//self.page_size+1} --")

    def switch_conversation(self, group_id):
        """
        切换到已有对话组，group_id 不变
        """
        if self._dirty:
            self.save()
        # 切换对话组时也新建连接，避免跨线程sqlite对象报错
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
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
        # 列出对话组时新建连接，避免跨线程sqlite对象报错
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
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

    def summarize_user_memory(self, period=None, n_messages=20):
        """
        生成记忆摘要，写入数据库和YAML
        :param period: 时间段描述（如'2024-06-01~2024-06-07'），可选
        :param n_messages: 选取最近多少条对话
        暂时默认提取末尾20条对话，后期可以改为根据用户画像中的last_active字段，提取最近n_messages条对话
        """
        # 生成prompt时新建连接，避免跨线程sqlite对象报错
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT content FROM conversations WHERE user_id=? ORDER BY id DESC LIMIT ?",
                (self.user_id, n_messages)
            )
            rows = cursor.fetchall()
        history = "\n".join([r[0] for r in reversed(rows)])
        # 生成prompt
        prompt = f"""You are a smart life assistant for Japanese students/workers, please summarize the main concerns, interests, problems, action plans, habits, emotional states of the user based on the following conversation history. Please combine Japanese daily life, study, work, visa, social, health, travel, etc. themes, and try to summarize as detailed as possible. If something cannot be inferred from the conversation, please output NULL.\n\nConversation history:\n{history}\n\nPlease strictly output the following JSON format, without any explanation, code block mark or other content. For example:\n{{\n  \"Main Concerns\": \"...\",\n  \"Interests\": \"...\",\n  ...\n}}"""
        summary_text = call_openai(prompt)
        summary_dict = parse_memory_summary_from_llm(summary_text)
        now = datetime.now().strftime("%Y-%m-%d")
        # 写入数据库
        # 写入数据库时新建连接，避免跨线程sqlite对象报错
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memory_summaries (user_id, period, summary, created_at, revised_by_user, revised_content, revised_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.user_id, period or "recent", summary_text, now, 0, "", None)
            )
            conn.commit()
        # 写入YAML
        memory_path = Path(__file__).parent.parent / "memory" / "user_memory.yaml"
        if memory_path.exists():
            with open(memory_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            for u in data.get("users", []):
                if u["user_profile"]["user_id"] == self.user_id:
                    if "memory_summaries" not in u:
                        u["memory_summaries"] = []
                    u["memory_summaries"].append({
                        "summary_id": int(now.replace("-", "")),
                        "period": period or "recent",
                        "summary": summary_text,
                        "created_at": now,
                        "revised_by_user": False,
                        "revised_content": "",
                        "revised_at": None
                    })
            with open(memory_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)

    def manual_profile_entry(self):
        """
        Manual entry of user profile via command line, save to database and YAML
        """
        profile = {}
        for field in ["name", "age", "gender", "education", "occupation", "city", "interests", "language", "nationality"]:
            value = input(f"Please enter {field} (leave blank if unknown, use comma to separate interests/languages): ")
            if field in ["interests", "language"]:
                value = [v.strip() for v in value.split(",") if v.strip()] if value else []
            profile[field] = value or None
        # 写入数据库时新建连接，避免跨线程sqlite对象报错
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET name=?, age=?, gender=?, education=?, occupation=?, city=?, interests=?, language=?, nationality=? WHERE id=?",
                (
                    profile.get("name"), profile.get("age"), profile.get("gender"), profile.get("education"),
                    profile.get("occupation"), profile.get("city"), ",".join(profile.get("interests", [])), ",".join(profile.get("language", [])),
                    profile.get("nationality"), self.user_id
                )
            )
            conn.commit()
        # 写入YAML
        memory_path = Path(__file__).parent.parent / "memory" / "user_memory.yaml"
        if memory_path.exists():
            with open(memory_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            for u in data.get("users", []):
                if u["user_profile"]["user_id"] == self.user_id:
                    u["user_profile"].update(profile)
            with open(memory_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)

    def auto_generate_profile(self, n_messages=30):
        """
        自动生成用户画像，写入数据库和YAML
        """
        # 查询历史消息时新建连接，避免跨线程sqlite对象报错
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT content FROM conversations WHERE user_id=? ORDER BY id DESC LIMIT ?",
                (self.user_id, n_messages)
            )
            rows = cursor.fetchall()
        history = "\n".join([r[0] for r in reversed(rows)])
        prompt = f"""You are a smart life assistant for Japanese students/workers, please infer and structure output the basic profile information of the user based on the following conversation history. Each field will output NULL if it cannot be inferred. Output in JSON format.\n\nFields include:\n- Name\n- Age\n- Gender\n- Education\n- Occupation\n- City\n- Interests (List)\n- Language (List)\n- Nationality\n- Contact Information\n- Common Apps (e.g., WeChat, Line, etc.)\n- Lifestyle Preferences (e.g., Diet, Routine, Exercise, etc.)\n\nConversation history:\n{history}\n\nPlease strictly output the following JSON format, without any explanation, code block mark or other content. For example:\n{{\n  \"Name\": \"Zhang San\",\n  \"Age\": 24,\n  ...\n}}"""
        profile_json = call_openai(prompt)
        print("[DEBUG] LLM returned content:", profile_json)  # Debug use
        try:
            profile_dict = parse_user_profile_from_llm(profile_json)
        except Exception as e:
            print("Failed to generate user profile, LLM returned content cannot be parsed as JSON. Please try again or check the Prompt.")
            print("Original return:", profile_json)
            return
        # Fallback processing: Use LLM results first, if None, then try to read original user_profile from YAML, if still None, use default values
        memory_path = Path(__file__).parent.parent / "memory" / "user_memory.yaml"
        yaml_profile = {}
        if memory_path.exists():
            with open(memory_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            for u in data.get("users", []):
                if u["user_profile"]["user_id"] == self.user_id:
                    yaml_profile = u["user_profile"]
                    break
        # Fallback logic for NOT NULL fields
        name = profile_dict.get("name") or yaml_profile.get("name") or "Unknown"
        age = profile_dict.get("age") or yaml_profile.get("age") or 0
        # ... Other fields can be fallback as needed ...
        # 更新数据库时新建连接，避免跨线程sqlite对象报错
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET name=?, age=?, gender=?, education=?, occupation=?, city=?, interests=?, language=?, nationality=?, extra_information=? WHERE id=?",
                (
                    name,
                    age,
                    profile_dict.get("gender") or yaml_profile.get("gender"),
                    profile_dict.get("education") or yaml_profile.get("education"),
                    profile_dict.get("occupation") or yaml_profile.get("occupation"),
                    profile_dict.get("city") or yaml_profile.get("city"),
                    ",".join(profile_dict.get("interests", [])) if profile_dict.get("interests") else ",".join(yaml_profile.get("interests", [])) if yaml_profile.get("interests") else None,
                    ",".join(profile_dict.get("language", [])) if profile_dict.get("language") else ",".join(yaml_profile.get("language", [])) if yaml_profile.get("language") else None,
                    profile_dict.get("nationality") or yaml_profile.get("nationality"),
                    json.dumps(profile_dict.get("extra_information"), ensure_ascii=False) if profile_dict.get("extra_information") else None,
                    self.user_id
                )
            )
            conn.commit()
        # 写入YAML
        memory_path = Path(__file__).parent.parent / "memory" / "user_memory.yaml"
        if memory_path.exists():
            with open(memory_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            for u in data.get("users", []):
                if u["user_profile"]["user_id"] == self.user_id:
                    u["user_profile"].update(profile_dict)
            with open(memory_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)