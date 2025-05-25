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
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
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
        self._register_signal()
        # self._dirty = False
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
        """
        开启新对话组，group_id 自增
        """
        if self._dirty:
            self.save()
        self.group_id = self._get_latest_group_id() + 1
        self._init_messages(is_new=True)
        self._saved_message_count = 0

    def show_history(self, page=1):
        """
        分页显示对话历史，当前为正序分页（旧→新）。如需倒序分页，将下方注释取消。
        :param page: 页码，从1开始
        """
        msgs = [m for m in self.messages if m["role"] in ("user", "assistant") and not (isinstance(m["content"], str) and (m["content"].startswith("[用户画像]") or m["content"].startswith("[记忆摘要]")))]
        # msgs = list(reversed(msgs))  # 如需倒序分页（新→旧），取消本行注释
        total = len(msgs)
        start = (page-1)*self.page_size
        end = min(start+self.page_size, total)
        for idx, m in enumerate(msgs[start:end], start=start+1):
            print(f"[{idx}] {m['role']}: {m['content']}")
        print(f"-- 第{page}页，共{(total-1)//self.page_size+1}页 --")

    def switch_conversation(self, group_id):
        """
        切换到已有对话组，group_id 不变
        """
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

    def summarize_user_memory(self, period=None, n_messages=20):
        """
        生成记忆摘要，写入数据库和YAML
        :param period: 时间段描述（如'2024-06-01~2024-06-07'），可选
        :param n_messages: 选取最近多少条对话
        暂时默认提取末尾20条对话，后期可以改为根据用户画像中的last_active字段，提取最近n_messages条对话
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT content FROM conversations WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (self.user_id, n_messages)
        )
        rows = cursor.fetchall()
        history = "\n".join([r[0] for r in reversed(rows)])
        # 生成prompt
        prompt = f"""你是一个面向在日留学生/务工人员的智能生活助理，请根据以下对话历史，提炼出用户近期的主要关注点、兴趣爱好、困惑、行动计划、生活习惯、情绪状态等，生成一份结构化的记忆摘要。请结合日本生活、学习、工作、签证、社交、健康、出行等常见主题，尽量细致总结。如果某项无法从对话中推断，请输出NULL。\n\n对话历史如下：\n{history}\n\n请严格只输出如下 JSON 格式，不要输出任何解释、代码块标记或其它内容。例如：\n{{\n  \"主要关注点\": \"...\",\n  \"兴趣爱好\": \"...\",\n  ...\n}}"""
        summary_text = call_openai(prompt)
        summary_dict = parse_memory_summary_from_llm(summary_text)
        now = datetime.now().strftime("%Y-%m-%d")
        # 写入数据库
        cursor.execute(
            "INSERT INTO memory_summaries (user_id, period, summary, created_at, revised_by_user, revised_content, revised_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (self.user_id, period or "recent", summary_text, now, 0, "", None)
        )
        self.conn.commit()
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
        命令行交互手动录入用户画像，写入数据库和YAML
        """
        profile = {}
        for field in ["name", "age", "gender", "education", "occupation", "city", "interests", "language", "nationality"]:
            value = input(f"请输入{field}（可留空，兴趣/语言用逗号分隔）: ")
            if field in ["interests", "language"]:
                value = [v.strip() for v in value.split(",") if v.strip()] if value else []
            profile[field] = value or None
        # 写入数据库
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE users SET name=?, age=?, gender=?, education=?, occupation=?, city=?, interests=?, language=?, nationality=? WHERE id=?",
            (
                profile.get("name"), profile.get("age"), profile.get("gender"), profile.get("education"),
                profile.get("occupation"), profile.get("city"), ",".join(profile.get("interests", [])), ",".join(profile.get("language", [])),
                profile.get("nationality"), self.user_id
            )
        )
        self.conn.commit()
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
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT content FROM conversations WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (self.user_id, n_messages)
        )
        rows = cursor.fetchall()
        history = "\n".join([r[0] for r in reversed(rows)])
        prompt = f"""你是一个面向在日留学生/务工人员的智能生活助理，请根据以下对话历史，推断并结构化输出该用户的基本画像信息。每个字段如无法推断请输出NULL。输出为JSON格式。\n\n字段包括：\n- 姓名\n- 年龄\n- 性别\n- 学历\n- 职业\n- 城市\n- 兴趣（列表）\n- 语言（列表）\n- 国籍\n- 联系方式\n- 常用App（如微信、Line等）\n- 生活偏好（如饮食、作息、运动等）\n\n对话历史如下：\n{history}\n\n请严格只输出如下 JSON 格式，不要输出任何解释、代码块标记或其它内容。例如：\n{{\n  \"姓名\": \"张三\",\n  \"年龄\": 24,\n  ...\n}}"""
        profile_json = call_openai(prompt)
        print("[DEBUG] LLM返回内容：", profile_json)  # Debug用
        try:
            profile_dict = parse_user_profile_from_llm(profile_json)
        except Exception as e:
            print("用户画像生成失败，LLM返回内容无法解析为JSON。请重试或检查Prompt。")
            print("原始返回：", profile_json)
            return
        # 兜底处理：优先用 LLM 结果，如为 None，则尝试从 YAML 读取原有 user_profile 字段，如仍无则用默认值
        memory_path = Path(__file__).parent.parent / "memory" / "user_memory.yaml"
        yaml_profile = {}
        if memory_path.exists():
            with open(memory_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            for u in data.get("users", []):
                if u["user_profile"]["user_id"] == self.user_id:
                    yaml_profile = u["user_profile"]
                    break
        # 姓名、年龄等 NOT NULL 字段兜底逻辑
        name = profile_dict.get("name") or yaml_profile.get("name") or "未知"
        age = profile_dict.get("age") or yaml_profile.get("age") or 0
        # ... 其它字段可按需兜底 ...
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
        self.conn.commit()
        # 写入YAML
        memory_path = Path(__file__).parent.parent / "memory" / "user_memory.yaml"
        if memory_path.exists():
            with open(memory_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            for u in data.get("users", []):
                if u["user_profile"]["user_id"] == self.user_id:
                    for k in profile_dict:
                        if k != "extra_information":
                            u["user_profile"][k] = profile_dict[k]
                    if profile_dict.get("extra_information"):
                        u["user_profile"]["extra_information"] = profile_dict["extra_information"]
            with open(memory_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True)