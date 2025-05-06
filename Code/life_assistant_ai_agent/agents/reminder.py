# Reminder agent functions
import sqlite3
from flask import jsonify

def init_db():
    conn = sqlite3.connect('data/reminders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY, task TEXT, due_date TEXT)''')
    conn.commit()
    conn.close()

def add_reminder(task, due_date):
    if task and due_date:
        conn = sqlite3.connect('data/reminders.db')
        c = conn.cursor()
        c.execute("INSERT INTO reminders (task, due_date) VALUES (?, ?)", (task, due_date))
        conn.commit()
        conn.close()
        return jsonify({'status': 'Reminder added successfully'})
    return jsonify({'error': 'Invalid input'}), 400

def get_reminders():
    conn = sqlite3.connect('data/reminders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM reminders")
    reminders = c.fetchall()
    conn.close()
    return jsonify(reminders)