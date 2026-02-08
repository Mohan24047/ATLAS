# Database Module
# SQLite database setup and connection management

import sqlite3
import os
from datetime import datetime

# Database path (in atlas directory)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'memory.db')


def get_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create database and tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Facts table - for storing user preferences, info, etc.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facts (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            category TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Conversations table - for storing chat history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_text TEXT NOT NULL,
            assistant_text TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Tasks table - for storing user tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Notes table - for storing general notes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Reminders table - for storing timed alerts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            due_at TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            timestamp TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    return True


def get_timestamp():
    """Get current timestamp string."""
    return datetime.now().isoformat()


# Initialize database on module import
initialize_database()
