import sqlite3

def init_database():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def save_message(session_id, role, content):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO chat_messages(session_id, role, content)
        VALUES(?, ?, ?)
        """,
        (session_id, role, content)
        )
    
    conn.commit()
    conn.close()

def get_messages(session_id):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message_id, session_id, role, content
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY message_id
        """, (session_id,))

    rows = cursor.fetchall()
    
    messages = []

    for message_id, session_id, role, content in rows:
        messages.append({
            "role": role,
            "content": content
        })
        
    conn.close()
    return messages

def delete_messages(session_id):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM chat_messages WHERE session_id = ?",
        (session_id,)
        )

    conn.commit()
    conn.close()

def update_message(message_id, new_content):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE chat_messages
        SET content = ?
        WHERE message_id = ?
        """,
        (new_content, message_id)
    )

    conn.commit()
    conn.close()

def get_sessions():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT session_id
        FROM chat_messages
        ORDER BY session_id
    """)

    rows = cursor.fetchall()

    sessions = []

    for row in rows:
        sessions.append(row[0])

    conn.close()

    return sessions
