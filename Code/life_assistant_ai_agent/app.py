# Main entry point for Streamlit App

import streamlit as st
import os
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="AI Life Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
st.markdown("欢迎使用您的个人AI助手！")

# 根据选择的页面显示不同内容
if page == "主页":
    st.header("今日概览")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="待办事项", value="3", delta="+1")
    with col2:
        st.metric(label="已完成", value="5", delta="+2")
    with col3:
        st.metric(label="记忆条目", value="12", delta="+3")
        
elif page == "提醒事项":
    st.header("提醒事项管理")
    st.text_input("添加新提醒")
    st.button("添加")
    
elif page == "记忆管理":
    st.header("记忆管理")
    st.text_area("添加新记忆")
    st.button("保存")
    
elif page == "设置":
    st.header("设置")
    st.text_input("OpenAI API Key", type="password")
    st.button("保存设置")
