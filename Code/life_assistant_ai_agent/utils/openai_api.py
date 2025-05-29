import openai
import os

# =================== 旧实现 ===================
# def call_openai(prompt):
#     api_key = os.getenv("OPENAI_API_KEY")
#     client = openai.OpenAI(api_key=api_key)
#     response = client.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": "你是一个中文生活助理，善于总结和建议。"},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.7,
#         max_tokens=512
#     )
#     return response.choices[0].message.content.strip()
# 说明：旧实现只支持 content 为字符串，遇到多轮对话或新版 SDK 时会因缺少 type 字段报错。

# =================== 新实现 ===================
def _convert_message(msg):
    # 如果 content 已经是 list（新版格式），直接返回
    if isinstance(msg["content"], list):
        return msg
    # 否则转为新版格式
    return {
        "role": msg["role"],
        "content": [{"type": "text", "text": msg["content"]}]
    }

def call_openai(messages):
    """
    兼容新版 openai>=1.0.0 SDK 的消息格式，自动将 content 转为 [{type: "text", text: ...}]。
    支持多轮历史和新版 SDK。
    """
    api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key)
    # 如果传入的是字符串 prompt，自动转为单轮消息
    if isinstance(messages, str):
        messages = [
            {"role": "system", "content": "你是一个中文生活助理，善于总结和建议。"},
            {"role": "user", "content": messages}
        ]
    # 统一转换所有消息
    messages = [_convert_message(m) for m in messages]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=512
    )
    return response.choices[0].message.content.strip()