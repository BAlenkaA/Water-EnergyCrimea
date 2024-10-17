import datetime
import logging
import os
import re
from urllib.parse import urljoin

import requests
import requests_cache
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from configs import configure_logging
from energy import get_url_energy, send_energy_message
from exceptions import ParserFindTagException, find_tag, get_response
from water import check_water_and_send

load_dotenv()

TOKEN = os.getenv('TELTOK')
CHANNEL_ID = os.getenv('TEL_CHEL')

ENERGY_URL = 'https://crimea-energy.ru'


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    session = requests_cache.CachedSession()
    session.cache.clear()

    try:

        check_water_and_send(datetime.date.today().strftime('%d'), session)
        check_water_and_send((datetime.datetime.today()
                              + datetime.timedelta(days=1)
                              ).strftime('%d'), session)
        link = get_url_energy(session)
        send_energy_message(link, session)
    except ParserFindTagException as e:
        logging.error(f'Ошибка при выполнении парсинга: {e}')
    except Exception as e:
        logging.exception(f'Произошла ошибка: {e}', stack_info=True)


if __name__ == "__main__":
    main()
