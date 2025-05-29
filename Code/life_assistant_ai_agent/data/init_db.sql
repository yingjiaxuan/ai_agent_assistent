-- 用户画像表（冷数据）
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    education TEXT,
    occupation TEXT,
    city TEXT,
    interests TEXT, -- 逗号分隔
    language TEXT,  -- 逗号分隔
    nationality TEXT,
    register_date TEXT,
    last_active TEXT
);

-- 对话历史表（热数据）
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    group_id INTEGER, -- 对话分组（如一次完整问答会话）
    role TEXT,        -- user/assistant
    content TEXT,
    timestamp TEXT,
    tags TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- 记忆摘要表（热数据）
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

-- 提醒事项/日程表（热数据）
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    description TEXT,
    due_date TEXT,
    priority TEXT, -- 高/中/低
    status TEXT,   -- 待办/已完成
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
); 