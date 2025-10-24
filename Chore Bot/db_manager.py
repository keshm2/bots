import sqlite3
import json
from datetime import datetime, timedelta
from contextlib import contextmanager
import os
import shutil

CHORES_DIR = './Chore Bot/chores'
CHORES_DB = os.path.join(CHORES_DIR, 'chores.db')

CANVAS_DIR = './Chore Bot/canvas'
CANVAS_DB = os.path.join(CANVAS_DIR, 'canvas.db')

@contextmanager
def get_chores_db():
    os.makedirs(CHORES_DIR, exist_ok = True)

    conn = sqlite3.connect(CHORES_DB)
    conn.row_factory = sqlite3.Row

    conn.execute('PRAGMA cache_size = -2000')
    conn.execute('PRAGMA temp_store = MEMORY')
    conn.execute('PRAGMA mmap_size = 0')
    conn.execute('PRAGMA page_size = 4096')

    try:
        yield conn
        conn.commit()
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()


@contextmanager
def get_canvas_db():
    os.makedirs(CANVAS_DIR, exist_ok = True)

    conn = sqlite3.connect(CANVAS_DB)
    conn.row_factory = sqlite3.Row

    conn.execute('PRAGMA cache_size = -2000')
    conn.execute('PRAGMA temp_store = MEMORY')
    conn.execute('PRAGMA mmap_size = 0')
    conn.execute('PRAGMA page_size = 4096')

    try:
        yield conn
        conn.commit()
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

def init_chores_database():
    os.makedirs(CHORES_DIR, exist_ok=True)
    
    if not os.path.exists(CHORES_DB):
        raise FileNotFoundError(
            f"❌ Chores database not found at {CHORES_DB}\n"
            f"Please create it manually:\n"
            f"  sqlite3 {CHORES_DB} < {os.path.join(CHORES_DIR, 'schema.sql')}"
        )
    
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        
        required_tables = ['chore_lists', 'chores', 'reminder_state']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            raise ValueError(
                f"❌ Missing tables in chores database: {', '.join(missing_tables)}\n"
                f"Please recreate the database using schema.sql"
            )
    
    print(f"✅ Chores database verified at {CHORES_DB}")


def init_canvas_database():
    os.makedirs(CANVAS_DIR, exist_ok=True)
    
    if not os.path.exists(CANVAS_DB):
        raise FileNotFoundError(
            f"❌ Canvas database not found at {CANVAS_DB}\n"
            f"Please create it manually:\n"
            f"  sqlite3 {CANVAS_DB} < {os.path.join(CANVAS_DIR, 'schema.sql')}"
        )
    
    with get_canvas_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        
        required_tables = ['user_settings', 'assignment_reminders', 'assignment_cache']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            raise ValueError(
                f"❌ Missing tables in canvas database: {', '.join(missing_tables)}\n"
                f"Please recreate the database using schema.sql"
            )
    
    print(f"✅ Canvas database verified at {CANVAS_DB}")


def init_all_databases():
    try:
        init_chores_database()
        init_canvas_database()
        print("✅ All databases ready")
    except (FileNotFoundError, ValueError) as e:
        print(str(e))
        raise

# ============================================
# CHORE DATABASE OPERATIONS
# ============================================

def create_chore_list(user_id: int, list_name: str, guild_id: int = None) -> int:
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chore_lists (user_id, list_name, guild_id)
            VALUES (?, ?, ?)
        ''', (user_id, list_name, guild_id))
        return cursor.lastrowid

def get_user_lists(user_id: int) -> list:
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, list_name, guild_id, 
                   (SELECT COUNT(*) FROM chores WHERE list_id = chore_lists.id) as chore_count
            FROM chore_lists
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_list_by_name(user_id: int, list_name: str) -> dict:
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM chore_lists
            WHERE user_id = ? AND list_name = ?
        ''', (user_id, list_name))
        row = cursor.fetchone()
        return dict(row) if row else None

def delete_chore_list(user_id: int, list_name: str) -> bool:
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM chore_lists
            WHERE user_id = ? AND list_name = ?
        ''', (user_id, list_name))
        return cursor.rowcount > 0

def add_chore(list_id: int, name: str, assigned_to: int, 
              chore_type: str, frequency_days: int = None, 
              due_date: datetime = None, next_due: datetime = None) -> int:
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chores (list_id, name, chore_type, assigned_to, 
                              frequency_days, due_date, next_due)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (list_id, name, chore_type, assigned_to, 
              frequency_days, 
              due_date.isoformat() if due_date else None,
              next_due.isoformat() if next_due else None))
        return cursor.lastrowid

def get_list_chores(list_id: int) -> list:
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM chores
            WHERE list_id = ?
            ORDER BY id
        ''', (list_id,))
        return [dict(row) for row in cursor.fetchall()]

def get_chore_by_position(list_id: int, position: int) -> dict:
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM chores
            WHERE list_id = ?
            ORDER BY id
            LIMIT 1 OFFSET ?
        ''', (list_id, position - 1))
        row = cursor.fetchone()
        return dict(row) if row else None

def complete_chore(chore_id: int, completed_at: datetime = None) -> bool:
    if not completed_at:
        completed_at = datetime.now()
    
    with get_chores_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM chores WHERE id = ?', (chore_id,))
        chore = dict(cursor.fetchone())
        
        if chore['chore_type'] == 'one_time':
            cursor.execute('''
                UPDATE chores
                SET completed = 1, completed_at = ?
                WHERE id = ?
            ''', (completed_at.isoformat(), chore_id))
        else:
            next_due = completed_at + timedelta(days=chore['frequency_days'])
            cursor.execute('''
                UPDATE chores
                SET last_completed = ?, next_due = ?
                WHERE id = ?
            ''', (completed_at.isoformat(), next_due.isoformat(), chore_id))
        
        return cursor.rowcount > 0

def update_chore(chore_id: int, **kwargs) -> bool:
    if not kwargs:
        return False
    
    set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [chore_id]
    
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE chores
            SET {set_clause}
            WHERE id = ?
        ''', values)
        return cursor.rowcount > 0

def delete_chore(chore_id: int) -> bool:
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM chores WHERE id = ?', (chore_id,))
        return cursor.rowcount > 0

def check_reminder_sent(chore_id: int, reminder_type: str) -> bool:
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM reminder_state
            WHERE chore_id = ? AND reminder_type = ?
        ''', (chore_id, reminder_type))
        return cursor.fetchone() is not None

def mark_reminder_sent(guild_id: int, chore_id: int, reminder_type: str):
    with get_chores_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO reminder_state (guild_id, chore_id, reminder_type)
            VALUES (?, ?, ?)
        ''', (guild_id, chore_id, reminder_type))

def get_due_chores(guild_id: int = None) -> list:
    with get_chores_db() as conn:
        cursor = conn.cursor()
        
        query = '''
            SELECT c.*, cl.list_name, cl.guild_id, cl.user_id
            FROM chores c
            JOIN chore_lists cl ON c.list_id = cl.id
            WHERE c.completed = 0
        '''
        
        if guild_id:
            query += ' AND cl.guild_id = ?'
            cursor.execute(query, (guild_id,))
        else:
            cursor.execute(query)
        
        return [dict(row) for row in cursor.fetchall()]


# ============================================
# CANVAS DATABASE OPERATIONS
# ============================================

def set_user_ics(user_id: int, ics_link: str, timezone: str = 'America/Los_Angeles'):
    with get_canvas_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_settings (user_id, ics_link, timezone)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                ics_link = excluded.ics_link,
                timezone = excluded.timezone
        ''', (user_id, ics_link, timezone))

def get_user_ics(user_id: int) -> str:
    with get_canvas_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT ics_link FROM user_settings WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return row['ics_link'] if row else None

def get_all_users_with_ics() -> list:
    with get_canvas_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, ics_link, timezone FROM user_settings WHERE ics_link IS NOT NULL')
        return [dict(row) for row in cursor.fetchall()]

def check_assignment_reminder_sent(user_id: int, event_id: str, reminder_type: str) -> bool:
    with get_canvas_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM assignment_reminders
            WHERE user_id = ? AND event_id = ? AND reminder_type = ?
        ''', (user_id, event_id, reminder_type))
        return cursor.fetchone() is not None

def mark_assignment_reminder_sent(user_id: int, event_id: str, reminder_type: str, fingerprint: str = None):
    with get_canvas_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO assignment_reminders (user_id, event_id, reminder_type, fingerprint)
            VALUES (?, ?, ?, ?)
        ''', (user_id, event_id, reminder_type, fingerprint))

def get_assignment_fingerprint(user_id: int, event_id: str) -> str:
    with get_canvas_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT fingerprint FROM assignment_reminders
            WHERE user_id = ? AND event_id = ?
            ORDER BY reminded_at DESC
            LIMIT 1
        ''', (user_id, event_id))
        row = cursor.fetchone()
        return row['fingerprint'] if row else None

def cache_assignment(user_id: int, event_id: str, title: str, due_date: datetime, 
                    url: str = None, description: str = None, fingerprint: str = None):
    with get_canvas_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO assignment_cache 
            (user_id, event_id, title, due_date, url, description, fingerprint, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, event_id, title, due_date.isoformat(), url, description, fingerprint, datetime.now().isoformat()))


# ============================================
# BACKUP FUNCTIONS
# ============================================



def backup_chores_database():
    backup_dir = os.path.join(CHORES_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'chores_backup_{timestamp}.db')
    
    shutil.copy2(CHORES_DB, backup_path)
    print(f"✅ Chores backup created: {backup_path}")
    return backup_path

def backup_canvas_database():
    backup_dir = os.path.join(CANVAS_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'canvas_backup_{timestamp}.db')
    
    shutil.copy2(CANVAS_DB, backup_path)
    print(f"✅ Canvas backup created: {backup_path}")
    return backup_path

def backup_all_databases():
    backup_chores_database()
    backup_canvas_database()