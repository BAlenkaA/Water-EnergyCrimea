import os
import re

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from exceptions import get_response

load_dotenv()

TOKEN = os.getenv('TELTOK')
CHANNEL_ID = os.getenv('TEL_CHEL')

WATER_URL = 'https://voda.crimea.ru/maintenance'


def check_water_maintenance(day, session):
    """
    Проверяет, есть ли новые сообщения, удовлетворяющие условиям на WATER_URL.
    Если сообщение есть, оно отправляется в телеграмм.
    """
    response = get_response(WATER_URL, session)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    date_element = soup.find(string=re.compile('^%s\\s...' % day))
    if date_element:
        link = date_element.parent
        for sibling in link.next_siblings:
            if sibling and hasattr(sibling, 'text'):
                if 'симфе' in sibling.text.lower():
                    next_sibling = sibling.next_sibling

                    if next_sibling and hasattr(next_sibling, 'text'):
                        if 'белое' in next_sibling.text.lower() or 'гридасова' in next_sibling.text.lower():
                            messages = f"{sibling.text} не будет воды {next_sibling.text}"
                            return messages
    return None
