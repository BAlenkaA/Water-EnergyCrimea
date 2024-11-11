import datetime
import logging
import time

import requests_cache
import schedule

from configs import configure_logging
from db import create_database
from energy import check_energy_repair_work
from exceptions import ParserFindTagException
from utils import send_telegram_message
from water import check_water_repair_work


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    create_database()
    session = requests_cache.CachedSession()
    session.cache.clear()
    today = datetime.date.today()
    try:
        for day in [
            today.strftime('%d'),
            (today + datetime.timedelta(days=1)).strftime('%d')
        ]:
            water_message = check_water_repair_work(day, session)
            if water_message:
                send_telegram_message(water_message, session)
        energy_message = check_energy_repair_work(today, session)
        if energy_message:
            send_telegram_message(energy_message, session)

        logging.info('Парсер ждет перезапуска!')
    except ParserFindTagException as e:
        logging.error(f'Ошибка при выполнении парсинга: {e}')
    except Exception as e:
        logging.exception(f'Произошла ошибка: {e}', stack_info=True)


for hour in range(9, 20):
    schedule.every().day.at(f"{hour:02}:00").do(main)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
