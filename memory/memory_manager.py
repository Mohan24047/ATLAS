# Memory Manager
# Provides CRUD operations for persistent memory

from memory.db import get_connection, get_timestamp


class MemoryManager:
    """Manages persistent memory operations."""
    
    # ==================== FACTS ====================
    
    def store_fact(self, key, value, category=None):
        """Store a new fact or update if exists."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO facts (key, value, category, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (key.lower(), value, category, get_timestamp()))
        conn.commit()
        conn.close()
        return True
    
    def update_fact(self, key, value):
        """Update an existing fact."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE facts SET value = ?, timestamp = ? WHERE key = ?
        ''', (value, get_timestamp(), key.lower()))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def delete_fact(self, key):
        """Delete a fact by key."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM facts WHERE key = ?', (key.lower(),))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def get_fact(self, key):
        """Get a specific fact by key."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value, category FROM facts WHERE key = ?', (key.lower(),))
        result = cursor.fetchone()
        conn.close()
        return {'value': result[0], 'category': result[1]} if result else None
    
    def list_facts(self):
        """List all stored facts."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value, category FROM facts ORDER BY timestamp DESC')
        results = cursor.fetchall()
        conn.close()
        return [{'key': r[0], 'value': r[1], 'category': r[2]} for r in results]
    
    # ==================== CONVERSATIONS ====================
    
    def store_conversation(self, user_text, assistant_text):
        """Store a conversation exchange."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (user_text, assistant_text, timestamp)
            VALUES (?, ?, ?)
        ''', (user_text, assistant_text, get_timestamp()))
        conn.commit()
        conn.close()
        return True
    
    def get_recent_conversations(self, limit=10):
        """Get recent conversations."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_text, assistant_text, timestamp 
            FROM conversations ORDER BY id DESC LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return [{'user': r[0], 'assistant': r[1], 'timestamp': r[2]} for r in reversed(results)]
    
    # ==================== TASKS ====================
    
    def add_task(self, task):
        """Add a new task."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (task, status, timestamp)
            VALUES (?, 'pending', ?)
        ''', (task, get_timestamp()))
        conn.commit()
        conn.close()
        return True
    
    def list_tasks(self, status=None):
        """List tasks, optionally filtered by status."""
        conn = get_connection()
        cursor = conn.cursor()
        if status:
            cursor.execute('SELECT id, task, status FROM tasks WHERE status = ?', (status,))
        else:
            cursor.execute('SELECT id, task, status FROM tasks ORDER BY timestamp DESC')
        results = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'task': r[1], 'status': r[2]} for r in results]
    
    def complete_task(self, task_id):
        """Mark a task as complete."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks SET status = 'completed', timestamp = ? WHERE id = ?
        ''', (get_timestamp(), task_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    # ==================== NOTES ====================
    
    def add_note(self, content):
        """Add a note."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notes (content, timestamp)
            VALUES (?, ?)
        ''', (content, get_timestamp()))
        conn.commit()
        conn.close()
        return True
    
    def list_notes(self, limit=20):
        """List recent notes."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, content FROM notes ORDER BY timestamp DESC LIMIT ?', (limit,))
        results = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'content': r[1]} for r in results]


    # ==================== REMINDERS ====================
    
    def add_reminder(self, message, due_at):
        """Add a new reminder."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reminders (message, due_at, status, timestamp)
            VALUES (?, ?, 'pending', ?)
        ''', (message, due_at, get_timestamp()))
        rid = cursor.lastrowid
        conn.commit()
        conn.close()
        return rid
    
    def list_pending_reminders(self):
        """List reminders that are pending."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, message, due_at FROM reminders WHERE status = 'pending' ORDER BY due_at ASC")
        results = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'message': r[1], 'due_at': r[2]} for r in results]
    
    def complete_reminder(self, reminder_id):
        """Mark a reminder as triggered/completed."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET status = 'completed' WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()
        return True


# Singleton instance
memory = MemoryManager()

