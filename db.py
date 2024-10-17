import sqlite3


def create_database():
    """Создает базу данных и таблицу для отправленных сообщений."""
    conn = sqlite3.connect('sent_messages.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT UNIQUE
        )
    ''')

    conn.commit()
    conn.close()


def message_exists(message):
    """Проверяет, существует ли сообщение в базе данных."""
    conn = sqlite3.connect('sent_messages.db')
    cursor = conn.cursor()

    cursor.execute('SELECT 1 FROM messages WHERE message = ?', (message,))
    exists = cursor.fetchone() is not None

    conn.close()
    return exists


def add_message(message):
    """Добавляет новое сообщение в базу данных."""
    conn = sqlite3.connect('sent_messages.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO messages (message) VALUES (?)', (message,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Если сообщение уже существует, ничего не делаем

    conn.close()
