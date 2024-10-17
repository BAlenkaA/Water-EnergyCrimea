import os

import requests
import logging

from dotenv import load_dotenv

from db import message_exists, add_message

load_dotenv()

TOKEN = os.getenv('TELTOK')
CHANNEL_ID = os.getenv('TEL_CHEL')


def send_telegram_message(message, session):
    """
    Отправляет сообщение в Телеграм.
    """
    if not message_exists(message):
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                params={"chat_id": CHANNEL_ID, "text": message}
            )
            response_json = response.json()
            if response_json.get("ok"):
                logging.info(f'Сообщение успешно отправлено: {message}')
                add_message(message)
            else:
                logging.error(f'Ошибка отправки сообщения: {response_json}')
            return response_json
        except requests.RequestException as e:
            logging.error(f'Ошибка при отправке сообщения: {e}')
            return None
