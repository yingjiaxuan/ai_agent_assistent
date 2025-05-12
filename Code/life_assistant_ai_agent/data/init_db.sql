-- 用户画像表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    education TEXT,
    occupation TEXT,
    city TEXT,
    interests TEXT,
    language TEXT,
    register_date TEXT,
    last_active TEXT
);

-- 对话历史表
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT, -- user/assistant
    content TEXT,
    timestamp TEXT,
    tags TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- 记忆摘要表
CREATE TABLE IF NOT EXISTS memory_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    period TEXT,
    summary TEXT,
    created_at TEXT,
    revised_by_user INTEGER,
    revised_content TEXT,
    revised_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
); 