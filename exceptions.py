import logging

from requests.exceptions import RequestException


class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


def get_response(url, session):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        response.raise_for_status()
        return response
    except RequestException:
        logging.error(
            f'Возникла ошибка при загрузке страницы {url}',
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
