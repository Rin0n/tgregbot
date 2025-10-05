import sqlite3
def init_db():
    conn = sqlite3.connect('userdata.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY, 
                full_name TEXT, 
                birth_date TEXT,
                phone TEXT,
                email TEXT)
                ''')
    conn.commit()
    cur.close()
    conn.close()
    
def save_user_data(id, full_name, birth_date, phone, email):
    conn = sqlite3.connect('userdata.db')
    cur = conn.cursor()
    cur.execute('''
                REPLACE INTO users(id, full_name, birth_date, phone, email)
                VALUES (?, ?, ?, ?, ?)
                ''',(id, full_name, birth_date, phone, email))
    conn.commit()
    cur.close()
    conn.close()

def get_user_data(id):
    conn = sqlite3.connect('userdata.db')
    cur = conn.cursor()
    cur.execute("SELECT full_name, birth_date, phone, email FROM users WHERE id = ?", (id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result