import datetime
import os
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELTOK')
CHANNEL_ID = os.getenv('TEL_CHEL')

ENERGY_URL = 'https://crimea-energy.ru'
WATER_URL = 'https://voda.crimea.ru/maintenance'


def check_water_and_send(day):
    """
    Checks if there are new messages that meet the conditions on the WATER_URL.
    If there is a message, it is sent to the telegram.
    """
    response = requests.get('https://voda.crimea.ru/maintenance')
    soup = BeautifulSoup(response.text, 'html.parser')
    if soup.find(string=re.compile('^%s\\s...' % day)) is not None:
        link = soup.find(string=re.compile('^%s\\s...' % day)).parent
        for sibling in link.next_siblings:
            if ('гридасова' in sibling.text.lower()
                    or 'белое' in sibling.text.lower()):
                print(requests.get(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id="
                    f"{CHANNEL_ID}&text={link.text + sibling.text}").json())


def get_url_energy():
    """
    Checks if there are new messages that satisfy the conditions on the ENERGY_URL.
    """
    relative_link = '/consumers/cserv/classifieds'
    response = requests.get(urljoin(ENERGY_URL, relative_link))
    soup_energy = BeautifulSoup(response.text, 'lxml')
    current_date = datetime.datetime.now().date()
    section_items = soup_energy.find_all(
        'div', class_=re.compile(r'^items-row cols-1'))
    for section in section_items:
        span_item = section.find('span')
        date_post = datetime.datetime.strptime(
            span_item.text.strip()[:10], "%d/%m/%Y").date()
        h5_item = section.find('h5')

        if (date_post == current_date
                and 'симферополю' in h5_item.text.strip().lower()):
            a_href = h5_item.find('a')
            return urljoin(ENERGY_URL, a_href['href'])


def send_energy_message(link):
    """
    Sends a message to telegram if the link is not None.
    """
    if link is not None:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, features='lxml')
        doc_a_tag = soup.find('a', attrs={'href': re.compile(r'\.doc$')})
        href = doc_a_tag['href']
        downloads_link = urljoin(ENERGY_URL, href)
        section_div = soup.find('div', attrs={'itemprop': 'articleBody'})
        p_item = section_div.find('p')
        text = p_item.text
        print(requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id="
            f"{CHANNEL_ID}&text="
            f"Электроэнергия:\n\n{text}\n{downloads_link}").json())


if __name__ == "__main__":
    check_water_and_send(datetime.date.today().strftime('%d'))
    check_water_and_send((datetime.datetime.today()
                          + datetime.timedelta(days=1)
                          ).strftime('%d'))
    link = get_url_energy()
    send_energy_message(link)
