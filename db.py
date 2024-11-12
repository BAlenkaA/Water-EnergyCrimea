import datetime
import logging
import sqlite3


def create_database():
    """Создает базу данных и таблицу для отправленных сообщений."""
    try:
        conn = sqlite3.connect('sent_messages.db')
        cursor = conn.cursor()

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        conn.commit()
        logging.info("База данных и таблица успешно созданы/проверены.")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при создании базы данных или таблицы: {e}")
    finally:
        conn.close()


def message_exists(message):
    """Проверяет, существует ли сообщение в базе данных."""
    try:
        conn = sqlite3.connect('sent_messages.db')
        cursor = conn.cursor()

        cursor.execute('SELECT 1 FROM messages WHERE message = ?', (message,))
        exists = cursor.fetchone() is not None

        return exists
    except sqlite3.Error as e:
        logging.error(f"Ошибка при проверке существования сообщения: {e}")
        return False  # В случае ошибки возвращаем False, чтобы не блокировать дальнейшую работу
    finally:
        conn.close()


def add_message(message):
    """Добавляет новое сообщение в базу данных."""
    try:
        conn = sqlite3.connect('sent_messages.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO messages (message) VALUES (?)', (message,))
        conn.commit()
        logging.info(f"Сообщение добавлено в базу данных: {message}")
    except sqlite3.IntegrityError:
        logging.info(f"Сообщение уже существует в базе данных: {message}")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при добавлении сообщения: {e}")
    finally:
        conn.close()


# Функция для удаления записей за вчерашний день
def delete_yesterday_messages():
    """Удаляет все записи из базы данных, которые были добавлены вчера."""
    try:
        conn = sqlite3.connect('sent_messages.db')
        cursor = conn.cursor()

        # Получаем дату вчерашнего дня
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        cursor.execute('''
                DELETE FROM messages
                WHERE DATE(created_at) = ?
            ''', (yesterday,))

        conn.commit()
        logging.info(f"Удалены записи за {yesterday}.")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при удалении записей за вчерашний день: {e}")
    finally:
        conn.close()
