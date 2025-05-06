# Main entry point for Streamlit App
import streamlit as st
import requests
import datetime

BASE_URL = 'http://127.0.0.1:5000'

st.set_page_config(page_title="AI Agent Web App", page_icon="🧠", layout="wide")

st.title('🌸 AI Agent Web App: Life Assistant for Living in Japan')

st.sidebar.title('📚 Navigation')
option = st.sidebar.radio('Choose a function', ['Add Reminder', 'View Reminders', 'Ask Question', 'View Memory', 'Life Suggestions'])

if option == 'Add Reminder':
    st.header('📝 Add a Reminder')
    task = st.text_input('Task')
    due_date = st.date_input('Due Date', min_value=datetime.date.today())
    if st.button('Add Reminder', key='add_reminder'):
        response = requests.post(f'{BASE_URL}/add_reminder', json={'task': task, 'due_date': due_date.strftime('%Y-%m-%d')})
        if response.status_code == 200:
            st.success('🎉 Reminder added successfully!')
        else:
            st.error('❌ Failed to add reminder.')

elif option == 'View Reminders':
    st.header('📅 View Reminders')
    response = requests.get(f'{BASE_URL}/get_reminders')
    if response.status_code == 200:
        reminders = response.json()
        for reminder in reminders:
            st.write(f'🔔 **Task**: {reminder[1]}, **Due Date**: {reminder[2]}')
    else:
        st.error('❌ Failed to fetch reminders.')

elif option == 'Ask Question':
    st.header('🤖 Ask a Question')
    question = st.text_input('Your Question', key='ask_question')
    if st.button('Ask', key='ask_button'):
        response = requests.post(f'{BASE_URL}/ask_question', json={'question': question})
        if response.status_code == 200:
            answer = response.json().get('answer')
            st.write(f'💡 **Answer**: {answer}')
        else:
            st.error('❌ Failed to get an answer.')

elif option == 'View Memory':
    st.header('🧠 View Memory')
    response = requests.get(f'{BASE_URL}/get_memory')
    if response.status_code == 200:
        memory = response.json()
        for entry in memory:
            st.write(f'❓ **Question**: {entry[1]}, 💡 **Answer**: {entry[2]}')
    else:
        st.error('❌ Failed to fetch memory.')

elif option == 'Life Suggestions':
    st.header('🗺️ Life Suggestions')
    response = requests.get(f'{BASE_URL}/get_life_suggestions')
    if response.status_code == 200:
        suggestions = response.json()
        for suggestion in suggestions:
            st.write(f'🌟 **Suggestion**: {suggestion}')
    else:
        st.error('❌ Failed to fetch life suggestions.')