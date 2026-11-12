import sqlite3

conn = sqlite3.connect("chat_history.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table'
    """)

print("테이블:", cursor.fetchall())

cursor.execute("PRAGMA table_info(chat_messages)")
print("컬럼:", cursor.fetchall())

cursor.execute("SELECT * FROM chat_messages")
print("데이터:", cursor.fetchall())

