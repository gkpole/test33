import sqlite3

conn = sqlite3.connect('db.db', check_same_thread=False)
cursor = conn.cursor()
def main():
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
user_id int NOT NULL UNIQUE,
text1 str,
text2 str,
text3 str,
confirm int);''')
def add_user(user_id: int):
    cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
def add_text1(text1: str, user_id1):
    cursor.execute(f'INSERT OR REPLACE INTO users (user_id, text1, text2, text3, confirm) VALUES (?,?,?,?,?)', (user_id1, text1, None, None, 0))
    conn.commit()
def add_text2(text1: str, text2: str, user_id1):
    cursor.execute(f'INSERT OR REPLACE INTO users (user_id, text1, text2, text3, confirm) VALUES (?,?,?,?,?)', (user_id1, text1, text2, None, 0))
    conn.commit()
def add_text3(text1: str, text2:str, text3: str, user_id1):
    cursor.execute(f'INSERT OR REPLACE INTO users (user_id, text1, text2, text3, confirm) VALUES (?,?,?,?,?)', (user_id1, text1, text2, text3, 0))
    conn.commit()
def add_confirm(text1: str, text2:str, text3: str, user_id1, confirm: int):
    cursor.execute(f'UPDATE users SET confirm={confirm} WHERE user_id = {user_id1}')
    conn.commit()
    
def get_conf(user_id1):
    cursor.execute(f'SELECT confirm FROM users WHERE user_id={user_id1}')
    jon = cursor.fetchone()
    return jon[0]
    
def get_text1(user_id1):
    cursor.execute(f'SELECT text1 FROM users WHERE user_id={user_id1}')
    jon = cursor.fetchone()
    return jon[0]
def get_text2(user_id1):
    cursor.execute(f'SELECT text2 FROM users WHERE user_id={user_id1}')
    jon = cursor.fetchone()
    return jon[0]
def get_zaya(user_id1):
    cursor.execute(f'SELECT * FROM users WHERE user_id={user_id1}')
    jon = cursor.fetchall()
    return jon[0][3]
if __name__ == '__main__':
    main()
