import sqlite3
from typing import List

# SQlite 轻量级储存
def init_db():
    """初始化数据库，如果表不存在就创建它。"""
    conn = sqlite3.connect("itachi_agent.db")
    cursor = conn.cursor()
    # 会话表：每一行记录一轮完整的对话（Human + AI）
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS sessions
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       session_id
                       TEXT
                       NOT
                       NULL,
                       human_message
                       TEXT
                       NOT
                       NULL,
                       ai_message
                       TEXT
                       NOT
                       NULL,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')
    # 为 session_id 创建索引，可以加速查询
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON sessions (session_id)')
    conn.commit()
    conn.close()
    print("对话历史加载完毕\n")


def save_conversation_round(session_id: str, human_message: str, ai_message: str):
    """保存一轮完整的对话（Human + AI）。"""
    conn = None
    try:
        conn = sqlite3.connect("itachi_agent.db")
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO sessions (session_id, human_message, ai_message)
                       VALUES (?, ?, ?)
                       ''', (session_id, human_message, ai_message))
        conn.commit()
    except sqlite3.OperationalError as error:
        print("发生数据库错误:",error)
    finally:
        if conn:
            conn.close()




def load_conversation_history(session_id: str) -> List[dict]:
    """加载某个会话的所有历史对话，返回一个消息字典列表。"""
    conn = sqlite3.connect("itachi_agent.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT human_message, ai_message, timestamp
                   FROM sessions
                   WHERE session_id = ?
                   ORDER BY timestamp ASC
                   ''', (session_id,))

    history = []
    for row in cursor.fetchall():
        # 把每一轮对话拆成两条独立的消息，方便直接放入 state["messages"]
        history.append({"role": "human", "content": row["human_message"]})
        history.append({"role": "ai", "content": row["ai_message"]})

    conn.close()
    return history