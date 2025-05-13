# Main entry point for Streamlit App

import streamlit as st
import os
import yaml
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="AI Life Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 读取用户画像和记忆摘要（示例：从yaml加载第一个用户）
def load_user_memory():
    memory_path = Path(__file__).parent / "memory" / "user_memory.yaml"
    if not memory_path.exists():
        return None
    with open(memory_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data or not data.get("users"):
        return None
    return data["users"][0]  # 默认展示第一个用户

user_data = load_user_memory()

# 自定义CSS样式
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    h1 {
        color: #1E88E5;
    }
    </style>
    """, unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.title("🤖 AI助手")
    st.markdown("---")
    
    # 导航菜单
    page = st.radio(
        "选择功能",
        ["主页", "提醒事项", "记忆管理", "设置"]
    )

# 主界面
st.title("AI Life Assistant")

# 根据选择的页面显示不同内容
if page == "主页":
    st.header("欢迎使用您的个人AI助手！")
    if user_data:
        st.subheader("用户画像")
        profile = user_data["user_profile"]
        st.markdown(f"**姓名：** {profile.get('name', '')}")
        st.markdown(f"**年龄：** {profile.get('age', '')}")
        st.markdown(f"**性别：** {profile.get('gender', '')}")
        st.markdown(f"**学历：** {profile.get('education', '')}")
        st.markdown(f"**职业：** {profile.get('occupation', '')}")
        st.markdown(f"**兴趣：** {', '.join(profile.get('interests', []))}")
        st.markdown(f"**语言：** {', '.join(profile.get('language', []))}")
        st.markdown(f"**国籍：** {profile.get('nationality', '')}")
        st.markdown(f"**最近活跃：** {profile.get('last_active', '')}")
    else:
        st.info("未找到用户画像信息。")

elif page == "提醒事项":
    st.header("提醒事项管理")
    if user_data and user_data.get("reminders"):
        for r in user_data["reminders"]:
            st.markdown(f"- **{r['title']}**（优先级：{r['priority']}，截止：{r['due_date']}） - {r['description']} [状态：{r['status']}]" )
    else:
        st.info("暂无提醒事项。")
    st.text_input("添加新提醒（演示功能）")
    st.button("添加")
    
elif page == "记忆管理":
    st.header("记忆体管理")
    if user_data and user_data.get("memory_summaries"):
        for m in user_data["memory_summaries"]:
            st.markdown(f"- **{m['period']}**：{m['summary']}")
    else:
        st.info("暂无记忆摘要。")
    st.text_area("添加新记忆（演示功能）")
    st.button("保存")
    
elif page == "设置":
    st.header("设置")
    st.text_input("OpenAI API Key", type="password")
    st.button("保存设置")
