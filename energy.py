import datetime
import logging
import os
import re
import subprocess
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from docx import Document

from exceptions import get_response, find_tag

ENERGY_URL = 'https://crimea-energy.ru'


def get_url_energy(day, session):
    """
    Проверяет, есть ли новые сообщения, удовлетворяющие условиям на ENERGY_URL.
    """
    relative_link = '/consumers/cserv/classifieds'
    energy_url = urljoin(ENERGY_URL, relative_link)
    response = get_response(energy_url, session)
    if response is None:
        return
    soup_energy = BeautifulSoup(response.text, 'lxml')
    current_date = day.strftime("%d/%m/%Y")
    section_items = soup_energy.find_all(
        'div', class_=re.compile(r'^items-row cols-1'))
    for section in section_items:
        span_item = find_tag(section, 'span')
        date_post = datetime.datetime.strptime(
            span_item.text.strip()[:10], "%d/%m/%Y").strftime("%d/%m/%Y")
        h5_item = find_tag(section, 'h5')
        if (date_post == current_date
                and 'симферо' in h5_item.text.strip().lower()):
            a_href = find_tag(h5_item, 'a')
            link = urljoin(ENERGY_URL, a_href['href'])
            logging.info(
                'Ссылка на страницу, соответствующую критериям, и содержащую ссылку на файл получена')
            response = get_response(link, session)
            soup = BeautifulSoup(response.text, features='lxml')
            doc_a_tag = find_tag(soup, 'a', attrs={'href': re.compile(r'\.doc$')})
            href = doc_a_tag['href']
            downloads_link = urljoin(ENERGY_URL, href)
            return downloads_link
    logging.info('Нет страниц, соответствующих критериям поиска')


def download_doc(url):
    """
       Скачивает .doc файл по URL и сохраняет его в директорию docs в корне проекта.
       """
    try:
        # Определяем директорию для сохранения .doc файла (в корне проекта /docs)
        project_root = os.path.dirname(os.path.abspath(__file__))  # Корень проекта
        docs_dir = os.path.join(project_root, 'docs')  # Путь к директории docs

        # Проверяем, существует ли директория docs, если нет - создаем
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)

        # Генерируем уникальное имя файла с сохранением расширения .doc
        file_name = os.path.join(docs_dir, os.path.basename(url).split("?")[0] or "downloaded_file.doc")

        # Скачиваем файл
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(response.content)
            logging.info(f"Файл успешно загружен и сохранен как {file_name}")
            return file_name
        else:
            logging.error(f"Не удалось скачать файл {url}, статус {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла: {e}")
        return None


def convert_doc_to_docx(doc_file_path):
    """
    Конвертирует .doc файл в .docx с использованием LibreOffice и сохраняет в директорию docxs в корне проекта.
    """
    try:
        # Определяем директорию для сохранения .docx файла (в корне проекта /docs)
        project_root = os.path.dirname(os.path.abspath(__file__))  # Корень проекта
        docs_dir = os.path.join(project_root, 'docxs')  # Путь к директории docs

        # Проверяем, существует ли директория docs, если нет - создаем
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
        # Формируем путь для сохранения конвертированного файла в /docs
        output_file_name = os.path.basename(doc_file_path).replace('.doc', '.docx')  # Имя файла .docx
        output_file_path = os.path.join(docs_dir, output_file_name)  # Полный путь к файлу .docx

        # Выполняем команду конвертации с сохранением в директорию docs
        subprocess.run(['libreoffice', '--headless', '--convert-to', 'docx', '--outdir',
                        docs_dir, doc_file_path], check=True)

        # Проверяем, что файл был создан
        if os.path.exists(output_file_path):
            return output_file_path
        else:
            logging.error(f"Конвертация не удалась: {output_file_path} не найден.")
            return None
    except Exception as e:
        logging.error(f"Ошибка при конвертации .doc в .docx: {e}")
        return None


def search_in_docx_text(docx_file_path, date):
    """
    Ищет строки в .docx файле с указанной датой и улицей.
    """
    matched_rows = []
    day = date.strftime("%d.%m.%Y")
    try:
        doc = Document(docx_file_path)

        for table in doc.tables:
            for row in table.rows:
                cell1 = row.cells[0].text
                cell2 = row.cells[1].text.replace('\n', '')
                cell3 = row.cells[2].text.replace('\n', '')
                if (day in cell1 or day in cell2) and ('Белое' in cell2 or 'Белое' in cell3):
                    matched_rows.append([cell1, cell2, cell3])
        return matched_rows
    except Exception as e:
        logging.error(f"Ошибка при парсинге .docx файла: {e}")
    return None


def check_energy_repair_work(day, session):
    link = get_url_energy(day, session)
    if link:
        doc_file = download_doc(link)
        if doc_file:
            docx_file = convert_doc_to_docx(doc_file)
            if docx_file:
                data_today = search_in_docx_text(docx_file, day)
                data_tomorrow = search_in_docx_text(docx_file, day + datetime.timedelta(days=1))
                messages = []
                for data in [data_today, data_tomorrow]:
                    if data:
                        messages.extend(data)
                output_message = '\n\n'.join([f"{item[0]}\n{item[1].replace(';', ';\n')}" for item in messages])
                return f'Внимание, отключение электричества: {output_message}'
            else:
                logging.error("Ошибка: конвертация .doc в .docx не удалась.")
        else:
            logging.error("Ошибка: не удалось скачать .doc файл.")
