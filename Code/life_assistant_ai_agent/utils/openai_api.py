import openai
import os

def call_openai(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一个中文生活助理，善于总结和建议。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=512
    )
    return response.choices[0].message.content.strip()