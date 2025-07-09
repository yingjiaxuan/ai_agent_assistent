# Main entry point for Streamlit App

import streamlit as st
import os
import yaml
import sqlite3
from pathlib import Path
from agents.memory_agent import MemoryAgent
from config import DATABASE_PATH

# 设置页面配置
st.set_page_config(
    page_title="AI Life Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 多语言文本配置
TEXTS = {
    "en": {
        "page_title": "AI Life Assistant",
        "sidebar_title": "🤖 AI Assistant",
        "home": "Home",
        "reminders": "Reminders",
        "memory_management": "Memory Management",
        "settings": "Settings",
        "welcome_message": "Welcome to your personal AI assistant!",
        "user_profile": "User Profile",
        "name": "Name",
        "age": "Age",
        "gender": "Gender",
        "education": "Education",
        "occupation": "Occupation",
        "interests": "Interests",
        "language": "Language",
        "nationality": "Nationality",
        "last_active": "Last Active",
        "no_user_profile": "No user profile information found.",
        "reminder_management": "Reminder Management",
        "no_reminders": "No reminders available.",
        "add_new_reminder": "Add New Reminder (Demo Feature)",
        "add": "Add",
        "memory_management_title": "Memory Management",
        "no_memory_summaries": "No memory summaries available.",
        "add_new_memory": "Add New Memory (Demo Feature)",
        "save": "Save",
        "settings_title": "Settings",
        "openai_api_key": "OpenAI API Key",
        "save_settings": "Save Settings",
        "language_switch": "Language",
        "select_function": "Select Function",
        "exit": "Exit",
        "user_id": "User ID",
        "switch_user": "Switch User",
        "chat_placeholder": "Type your message here...",
        "send": "Send",
        "new_conversation": "New Conversation",
        "conversation_history": "Conversation History",
        "no_conversation_history": "No conversation history available.",
        "current_user": "Current User",
        "available_users": "Available Users",
        "select_user": "Select User",
        "chat_interface": "Chat Interface",
        "type_question": "Type your question to start chatting"
    },
    "zh": {
        "page_title": "AI 生活助手",
        "sidebar_title": "🤖 AI助手",
        "home": "主页",
        "reminders": "提醒事项",
        "memory_management": "记忆管理",
        "settings": "设置",
        "welcome_message": "欢迎使用您的个人AI助手！",
        "user_profile": "用户画像",
        "name": "姓名",
        "age": "年龄",
        "gender": "性别",
        "education": "学历",
        "occupation": "职业",
        "interests": "兴趣",
        "language": "语言",
        "nationality": "国籍",
        "last_active": "最近活跃",
        "no_user_profile": "未找到用户画像信息。",
        "reminder_management": "提醒事项管理",
        "no_reminders": "暂无提醒事项。",
        "add_new_reminder": "添加新提醒（演示功能）",
        "add": "添加",
        "memory_management_title": "记忆体管理",
        "no_memory_summaries": "暂无记忆摘要。",
        "add_new_memory": "添加新记忆（演示功能）",
        "save": "保存",
        "settings_title": "设置",
        "openai_api_key": "OpenAI API Key",
        "save_settings": "保存设置",
        "language_switch": "语言",
        "select_function": "选择功能",
        "exit": "退出",
        "user_id": "用户ID",
        "switch_user": "切换用户",
        "chat_placeholder": "在此输入您的消息...",
        "send": "发送",
        "new_conversation": "新对话",
        "conversation_history": "对话历史",
        "no_conversation_history": "暂无对话历史。",
        "current_user": "当前用户",
        "available_users": "可用用户",
        "select_user": "选择用户",
        "chat_interface": "聊天界面",
        "type_question": "输入您的问题开始聊天"
    }
}

# 初始化会话状态
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'current_user_id' not in st.session_state:
    st.session_state.current_user_id = 1
if 'memory_agent' not in st.session_state:
    st.session_state.memory_agent = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def get_text(key):
    """获取当前语言的文本"""
    return TEXTS[st.session_state.language][key]

def get_available_users():
    """从数据库获取可用用户列表"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users ORDER BY id")
        users = cursor.fetchall()
        conn.close()
        return users
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return []

def initialize_memory_agent(user_id):
    """初始化记忆代理"""
    try:
        return MemoryAgent(user_id)
    except Exception as e:
        st.error(f"Error initializing memory agent: {e}")
        return None

def load_user_memory(user_id):
    """读取指定用户的画像和记忆摘要"""
    memory_path = Path(__file__).parent / "memory" / "user_memory.yaml"
    if not memory_path.exists():
        return None
    with open(memory_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data or not data.get("users"):
        return None
    for user in data["users"]:
        if user["user_profile"]["user_id"] == user_id:
            return user
    return None

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
    .top-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 10px;
        margin: 5px 0;
        border-radius: 10px;
    }
    .user-message {
        background-color: #e3f2fd;
        text-align: right;
    }
    .assistant-message {
        background-color: #f5f5f5;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# 顶部控制栏
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button(f"🚪 {get_text('exit')}"):
        st.success("已安全退出，请关闭本页面。\nSafely exited, please close this page.")
        st.stop()

with col2:
    if st.button(f"🌐 {get_text('language_switch')} / Language"):
        st.session_state.language = 'zh' if st.session_state.language == 'en' else 'en'
        st.rerun()

with col3:
    st.write(f"**{get_text('current_user')}:** {st.session_state.current_user_id}")

with col4:
    available_users = get_available_users()
    if available_users:
        user_options = {f"{user[1]} (ID: {user[0]})": user[0] for user in available_users}
        selected_user = st.selectbox(
            get_text("select_user"),
            options=list(user_options.keys()),
            index=0
        )
        new_user_id = user_options[selected_user]
        if new_user_id != st.session_state.current_user_id:
            st.session_state.current_user_id = new_user_id
            st.session_state.memory_agent = initialize_memory_agent(new_user_id)
            st.session_state.chat_history = []
            st.rerun()

# 侧边栏
with st.sidebar:
    st.title(get_text("sidebar_title"))
    st.markdown("---")
    
    # 导航菜单
    page = st.radio(
        get_text("select_function"),
        [get_text("home"), get_text("reminders"), get_text("memory_management"), get_text("settings")]
    )

# 主界面
st.title(get_text("page_title"))

# 根据选择的页面显示不同内容
if page == get_text("home"):
    st.header(get_text("welcome_message"))
    
    # 用户画像显示
    user_data = load_user_memory(st.session_state.current_user_id)
    if user_data:
        st.subheader(get_text("user_profile"))
        profile = user_data["user_profile"]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{get_text('name')}：** {profile.get('name', '')}")
            st.markdown(f"**{get_text('age')}：** {profile.get('age', '')}")
            st.markdown(f"**{get_text('gender')}：** {profile.get('gender', '')}")
            st.markdown(f"**{get_text('education')}：** {profile.get('education', '')}")
        with col2:
            st.markdown(f"**{get_text('occupation')}：** {profile.get('occupation', '')}")
            st.markdown(f"**{get_text('interests')}：** {', '.join(profile.get('interests', []))}")
            st.markdown(f"**{get_text('language')}：** {', '.join(profile.get('language', []))}")
            st.markdown(f"**{get_text('nationality')}：** {profile.get('nationality', '')}")
    else:
        st.info(get_text("no_user_profile"))
    
    st.markdown("---")
    
    # 聊天界面
    st.subheader(get_text("chat_interface"))
    
    # 初始化记忆代理
    if st.session_state.memory_agent is None:
        st.session_state.memory_agent = initialize_memory_agent(st.session_state.current_user_id)
    
    # 新对话按钮
    if st.button(get_text("new_conversation")):
        if st.session_state.memory_agent:
            st.session_state.memory_agent.new_conversation()
            st.session_state.chat_history = []
            st.success("New conversation started!")
    
    # 显示对话历史
    if st.session_state.chat_history:
        st.subheader(get_text("conversation_history"))
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message"><strong>AI:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    # 聊天输入
    st.markdown("---")
    st.write(get_text("type_question"))
    
    # 使用文本输入框进行聊天
    user_input = st.text_input(get_text("chat_placeholder"), key="chat_input")
    
    if st.button(get_text("send")):
        if user_input.strip():
            if st.session_state.memory_agent:
                try:
                    # 添加用户消息到历史
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    
                    # 获取AI回复
                    response = st.session_state.memory_agent.ask(user_input)
                    
                    # 添加AI回复到历史
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    # 保存对话
                    st.session_state.memory_agent.save()
                    
                    # 清空输入框并重新运行
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Memory agent not initialized")

elif page == get_text("reminders"):
    st.header(get_text("reminder_management"))
    user_data = load_user_memory(st.session_state.current_user_id)
    if user_data and user_data.get("reminders"):
        for r in user_data["reminders"]:
            st.markdown(f"- **{r['title']}**（优先级：{r['priority']}，截止：{r['due_date']}） - {r['description']} [状态：{r['status']}]" )
    else:
        st.info(get_text("no_reminders"))
    st.text_input(get_text("add_new_reminder"))
    st.button(get_text("add"))
    
elif page == get_text("memory_management"):
    st.header(get_text("memory_management_title"))
    user_data = load_user_memory(st.session_state.current_user_id)
    if user_data and user_data.get("memory_summaries"):
        for m in user_data["memory_summaries"]:
            st.markdown(f"- **{m['period']}**：{m['summary']}")
    else:
        st.info(get_text("no_memory_summaries"))
    st.text_area(get_text("add_new_memory"))
    st.button(get_text("save"))
    
elif page == get_text("settings"):
    st.header(get_text("settings_title"))
    st.text_input(get_text("openai_api_key"), type="password")
    st.button(get_text("save_settings"))
