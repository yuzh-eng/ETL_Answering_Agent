import sqlite3
import datetime
import os

DB_NAME = "etl_training.db"

def init_db():
    """Initializes the SQLite database and creates the training_logs table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS training_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            question_code TEXT NOT NULL,
            user_code TEXT NOT NULL,
            ai_feedback TEXT,
            is_correct BOOLEAN NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_training_log(user_id, pattern_type, question_code, user_code, ai_feedback, is_correct):
    """Saves a training session log to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO training_logs (user_id, pattern_type, question_code, user_code, ai_feedback, is_correct, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, pattern_type, question_code, user_code, ai_feedback, is_correct, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_mistakes(user_id):
    """Retrieves all failed attempts (mistakes) for a given user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT id, pattern_type, question_code, user_code, ai_feedback, created_at
        FROM training_logs
        WHERE user_id = ? AND is_correct = 0
        ORDER BY created_at DESC
    ''', (user_id,))
    mistakes = c.fetchall()
    conn.close()
    return mistakes

def get_all_logs(user_id):
    """Retrieves all logs for a given user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT id, pattern_type, question_code, user_code, ai_feedback, is_correct, created_at
        FROM training_logs
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    logs = c.fetchall()
    conn.close()
    return logs
