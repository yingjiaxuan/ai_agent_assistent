import json
import re

# 主字段定义，便于数据库和yaml同步
MAIN_PROFILE_FIELDS = [
    "name", "age", "gender", "education", "occupation", "city",
    "interests", "language", "nationality", "register_date", "last_active"
]

def extract_json_from_llm_output(text):
    """
    提取 LLM 输出中的 JSON 内容，兼容 markdown 代码块、纯 JSON、字符串包 JSON 等多种格式。
    """
    text = text.strip()
    # 1. 去除 markdown 代码块
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        text = match.group(1).strip()
    # 2. 如果是字符串包 JSON
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    # 3. 尝试解析
    return json.loads(text)

def parse_user_profile_from_llm(llm_json):
    """
    将LLM生成的用户画像JSON分配到主字段和extra_information
    :param llm_json: LLM输出的JSON字符串或dict
    :return: dict，主字段+extra_information
    """
    if isinstance(llm_json, str):
        data = extract_json_from_llm_output(llm_json)
    else:
        data = llm_json
    profile = {}
    extra = {}
    for k, v in data.items():
        if k in MAIN_PROFILE_FIELDS:
            profile[k] = v if v != "NULL" else None
        else:
            extra[k] = v
    profile["extra_information"] = extra if extra else None
    return profile

def parse_memory_summary_from_llm(llm_text):
    """
    解析LLM输出的记忆摘要（如有结构化JSON可直接用，否则按分段文本处理）
    """
    if isinstance(llm_text, str):
        try:
            return extract_json_from_llm_output(llm_text)
        except Exception:
            # fallback: 按分段文本解析
            return {"raw": llm_text}
    else:
        return llm_text 