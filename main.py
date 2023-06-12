import os

from bs4 import BeautifulSoup
import requests
import re
import datetime


def check_and_send(day):
    if soup.find(string=re.compile('^%s\\s...' % day)) is not None:
        link = soup.find(string=re.compile('^%s\\s...' % day)).parent
        for sibling in link.next_siblings:
            if 'бекира умерова' in sibling.text.lower() or 'хошкельды' in sibling.text.lower():
                print(requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHANNEL_ID}&text={link.text + sibling.text}").json())


response = requests.get('https://voda.crimea.ru/maintenance')
soup = BeautifulSoup(response.text, 'html.parser')
TOKEN = os.getenv('TELTOK')
CHANNEL_ID = os.getenv('TEL_CHEL')


if __name__ == "__main__":
    check_and_send(datetime.date.today().strftime('%d'))
    check_and_send((datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%d'))
