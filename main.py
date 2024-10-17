import datetime
import logging

import requests_cache

from configs import configure_logging
from db import create_database
from energy import get_url_energy, send_energy_message
from exceptions import ParserFindTagException
from utils import send_telegram_message
from water import check_water_maintenance


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    create_database()
    session = requests_cache.CachedSession()
    session.cache.clear()

    try:
        for day in [
            datetime.date.today().strftime('%d'),
            (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%d')
        ]:
            water_message = check_water_maintenance(day, session)
            if water_message:
                send_telegram_message(water_message, session)
        # link = get_url_energy(session)
        # send_energy_message(link, session)
        logging.info('Парсер ждет перезапуска!')
    except ParserFindTagException as e:
        logging.error(f'Ошибка при выполнении парсинга: {e}')
    except Exception as e:
        logging.exception(f'Произошла ошибка: {e}', stack_info=True)


if __name__ == "__main__":
    main()
