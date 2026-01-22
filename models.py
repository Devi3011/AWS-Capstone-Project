import sqlite3
import bcrypt
import json
from datetime import datetime
import uuid

class Database:
    def __init__(self, db_path="data/nexpersona.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                segment TEXT DEFAULT 'growth',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        ''')
        
        # Personalization sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                segment TEXT,
                signals JSON,
                experience_config JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Demo data
        cursor.execute("SELECT COUNT(*) FROM users WHERE email='demo@brand.com'")
        if cursor.fetchone()[0] == 0:
            demo_hash = bcrypt.hashpw("demo123".encode(), bcrypt.gensalt()).decode()
            cursor.execute(
                "INSERT INTO users (id, name, email, password_hash, segment) VALUES (?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), "Demo User", "demo@brand.com", demo_hash, "growth")
            )
        
        conn.commit()
        conn.close()
    
    def get_user_by_email(self, email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND active = 1", (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0], 'name': row[1], 'email': row[2],
                'segment': row[4], 'created_at': row[5]
            }
        return None
    
    def create_user(self, name, email, password, segment='growth'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if self.get_user_by_email(email):
            conn.close()
            return False
        
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_id = str(uuid.uuid4())
        
        cursor.execute(
            "INSERT INTO users (id, name, email, password_hash, segment) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, email, password_hash, segment)
        )
        conn.commit()
        conn.close()
        return True
    
    def verify_password(self, email, password):
        user = self.get_user_by_email(email)
        if not user:
            return False
        return bcrypt.checkpw(password.encode(), user['password_hash'].encode())
    
    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ? AND active = 1", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0], 'name': row[1], 'email': row[2],
                'segment': row[4], 'created_at': row[5]
            }
        return None
    
    def update_user_segment(self, user_id, segment):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET segment = ? WHERE id = ?", (segment, user_id))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def create_session(self, user_id, segment, signals, config):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        session_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO sessions (id, user_id, segment, signals, experience_config) VALUES (?, ?, ?, ?, ?)",
            (session_id, user_id, segment, json.dumps(signals), json.dumps(config))
        )
        conn.commit()
        conn.close()
        return session_id
