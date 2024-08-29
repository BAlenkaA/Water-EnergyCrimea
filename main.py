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
from exceptions import ParserFindTagException, find_tag, get_response

load_dotenv()

TOKEN = os.getenv('TELTOK')
CHANNEL_ID = os.getenv('TEL_CHEL')

ENERGY_URL = 'https://crimea-energy.ru'
WATER_URL = 'https://voda.crimea.ru/maintenancegaerga'


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


def get_url_energy(session):
    """
    Проверяет, есть ли новые сообщения, удовлетворяющие условиям на ENERGY_URL.
    """
    relative_link = '/consumers/cserv/classifieds'
    energy_url = urljoin(ENERGY_URL, relative_link)
    response = get_response(energy_url, session)
    if response is None:
        return
    soup_energy = BeautifulSoup(response.text, 'lxml')
    current_date = datetime.datetime.now().date()
    section_items = soup_energy.find_all(
        'div', class_=re.compile(r'^items-row cols-1'))
    for section in section_items:
        span_item = find_tag(section, 'span')
        date_post = datetime.datetime.strptime(
            span_item.text.strip()[:10], "%d/%m/%Y").date()
        h5_item = find_tag(section, 'h5')

        if (date_post == current_date
                and 'симферополю' in h5_item.text.strip().lower()):
            a_href = find_tag(h5_item, 'a')
            logging.info(
                'Ссылка на страницу, соответствующую критериям, получена')
            return urljoin(ENERGY_URL, a_href['href'])
    logging.info('Нет страниц, соответствующих критериям поиска')


def send_energy_message(link, session):
    """
    Отправляет сообщение в телеграмм, если ссылка не None.
    """
    if link is not None:
        response = get_response(link, session)
        soup = BeautifulSoup(response.text, features='lxml')
        doc_a_tag = find_tag(soup, 'a', attrs={'href': re.compile(r'\.doc$')})
        href = doc_a_tag['href']
        downloads_link = urljoin(ENERGY_URL, href)
        section_div = find_tag(soup, 'div', attrs={'itemprop': 'articleBody'})
        p_item = find_tag(section_div, 'p')
        text = p_item.text
        print(requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id="
            f"{CHANNEL_ID}&text="
            f"Электроэнергия:\n\n{text}\n{downloads_link}").json())
        logging.info(
            f'Сообщение с ссылкой {downloads_link} было отправлено в чат')


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
