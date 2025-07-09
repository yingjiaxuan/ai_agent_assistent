#!/usr/bin/env python3
"""
数据库初始化脚本
确保数据库表结构和mock数据正确设置
"""
import sqlite3
import os
from pathlib import Path
from config import DATABASE_PATH

def init_database():
    """初始化数据库表结构和mock数据"""
    
    # 确保data目录存在
    data_dir = Path(DATABASE_PATH).parent
    data_dir.mkdir(exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 读取SQL初始化脚本
    init_sql_path = Path(__file__).parent / "data" / "init_db.sql"
    mock_sql_path = Path(__file__).parent / "data" / "mock_data.sql"
    
    try:
        # 执行表结构初始化
        if init_sql_path.exists():
            with open(init_sql_path, 'r', encoding='utf-8') as f:
                init_sql = f.read()
            cursor.executescript(init_sql)
            print("✓ Database tables created successfully")
        
        # 检查是否已有数据
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0 and mock_sql_path.exists():
            # 插入mock数据
            with open(mock_sql_path, 'r', encoding='utf-8') as f:
                mock_sql = f.read()
            cursor.executescript(mock_sql)
            print("✓ Mock data inserted successfully")
        else:
            print(f"✓ Database already has {user_count} users")
        
        # 验证数据
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conv_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM reminders")
        reminder_count = cursor.fetchone()[0]
        
        print(f"✓ Database verification:")
        print(f"  - Users: {user_count}")
        print(f"  - Conversations: {conv_count}")
        print(f"  - Reminders: {reminder_count}")
        
        conn.commit()
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialization completed!") 