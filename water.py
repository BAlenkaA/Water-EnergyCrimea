import logging
import os
import re

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from exceptions import get_response

load_dotenv()

TOKEN = os.getenv('TELTOK')
CHANNEL_ID = os.getenv('TEL_CHEL')

WATER_URL = 'https://voda.crimea.ru/maintenance'


def check_water_and_send(day, session):
    """
    Проверяет, есть ли новые сообщения, удовлетворяющие условиям на WATER_URL.
    Если сообщение есть, оно отправляется в телеграмм.
    """
    response = get_response(WATER_URL, session)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    if soup.find(string=re.compile('^%s\\s...' % day)) is not None:
        link = soup.find(string=re.compile('^%s\\s...' % day)).parent
        for sibling in link.next_siblings:
            if ('гридасова' in sibling.text.lower()
                    or 'белое' in sibling.text.lower()):
                print(requests.get(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id="
                    f"{CHANNEL_ID}&text={link.text + sibling.text}").json())
                logging.info(f'Сообщение {link.text + sibling.text} '
                             f'было отправлено в чат')
