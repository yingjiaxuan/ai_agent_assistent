# Memory agent functions
import openai
import sqlite3
from flask import jsonify
import yaml

openai.api_key = 'YOUR_OPENAI_API_KEY'

def init_memory_db():
    conn = sqlite3.connect('data/reminders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY, question TEXT, answer TEXT)''')
    conn.commit()
    conn.close()

def ask_question(question):
    if question:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=question,
            max_tokens=100
        )
        answer = response.choices[0].text.strip()
        conn = sqlite3.connect('data/reminders.db')
        c = conn.cursor()
        c.execute("INSERT INTO memory (question, answer) VALUES (?, ?)", (question, answer))
        conn.commit()
        conn.close()
        return jsonify({'question': question, 'answer': answer})
    return jsonify({'error': 'Invalid input'}), 400

def get_memory():
    conn = sqlite3.connect('data/reminders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM memory")
    memory = c.fetchall()
    conn.close()
    return jsonify(memory)

def save_memory_to_yaml():
    conn = sqlite3.connect('data/reminders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM memory")
    memory = c.fetchall()
    conn.close()
    
    memory_dict = [{'question': entry[1], 'answer': entry[2]} for entry in memory]
    with open('memory/user_memory.yaml', 'w') as file:
        yaml.dump(memory_dict, file)