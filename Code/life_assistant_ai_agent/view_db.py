#!/usr/bin/env python3
"""
简单的数据库查看工具
"""
import sqlite3
import os
from config import DATABASE_PATH

def view_database():
    """查看数据库结构和内容"""
    if not os.path.exists(DATABASE_PATH):
        print(f"数据库文件不存在：{DATABASE_PATH}")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("=" * 50)
    print("📊 数据库概览")
    print("=" * 50)
    
    # 查看所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"📋 数据库表：{len(tables)} 个")
    for table in tables:
        print(f"  - {table[0]}")
    
    print("\n" + "=" * 50)
    print("📝 各表数据统计")
    print("=" * 50)
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"📊 {table_name}: {count} 条记录")
        
        # 显示前3条记录作为示例
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"   列名: {', '.join(columns)}")
            for i, row in enumerate(rows, 1):
                print(f"   示例 {i}: {row}")
        print()
    
    conn.close()

if __name__ == "__main__":
    view_database()
