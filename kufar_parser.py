import re
from dataclasses import astuple
import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from environs import Env
from pprint import pprint

from models import Item
from DB_client import DB_Postgres

env = Env()
env.read_env()
db_name = env('DBNAME')
db_user = env('DBUSER')
db_password = env('DBPASSWORD')
db_host = env('HOST')
db_port = env('PORT')

class ParserNotebook:
    # Данные для авторизации на сайте
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}

    DB = DB_Postgres(db_name, db_user, db_password, db_host, db_port)

    @classmethod
    def get_soup(cls, url: str) -> BeautifulSoup:
        """
        Функция подключения и получения кода страницы.
        :param url: URL страницы к которой подключаемся
        :return: возвращает данные страницы
        """
        response = requests.get(url, headers=cls.HEADERS)
        print(f'{response.status_code} | {url}')
        soup = BeautifulSoup(response.text, 'lxml')

        return soup

    @staticmethod
    def __get_item_links(soup: BeautifulSoup) -> list:
        """
        Функция сбора ссылок объявлений с каждой страницы раздела
        :param soup: BeautifulSoup страницы раздела
        :return: возвращает список urls объявлений
        """

        sections = soup.find_all('section')
        links = []
        for section in sections:
            # Выполняем проверку имеет-ли товар установленную стоимость
            link = section.find('a', href=True)['href'].split('?')[0]
            price = section.find('p', class_='styles_price__G3lbO')
            # Достаем цену со скидкой
            if not price:
                price = section.find('span', class_='styles_price__vIwzP').text
            else:
                price = price.text
            price = re.sub(r"[^0-9]", "", price)
            # Проверяем, если цена установлена, то добавляем ссылку в список
            if price.isdigit():
                links.append(link)

        # Достаем ссылку следующей страницы с объявлениями (по пагинации) из API
        json_data = soup.find('script', id='__NEXT_DATA__').text
        data = json.loads(json_data)['props']['initialState']['listing']['pagination']
        try:
            next_page_token = list(filter(lambda el: el['label'] == 'next', data))[0]['token'].replace('=', '%3D')
        except Exception as e:
            next_page_token = ''

        return [links, next_page_token]

    def __get_data(self, soup: BeautifulSoup, url: str) -> Item:
        """
        Функция сбора данный по объявлению
        :param soup: BeautifulSoup страницы объявления
        :param url: url страницы объявления
        :return: экземпляр класса Item - данные по одному ноутбуку
        """
        # Задаем параметрический словарь где ключь это data-name из кода страницы, а значение это название переменной
        # в датаклассе и в БД
        pars_list = {'computers_laptop_brand': 'manufacturer',
                     'computers_laptop_diagonal': 'screen_diagonal',
                     'computers_laptop_resolution': 'screen_resolution',
                     'computers_laptop_os': 'operating_system',
                     'computers_laptop_processor': 'processor',
                     'computer_equipment_laptops_ram': 'ram',
                     'computers_laptop_videocard': 'video_card_type',
                     'computers_laptop_videocard_brand': 'video_card',
                     'computers_laptop_hdd_type': 'storage_type',
                     'computers_laptop_hdd_volume': 'storage_capacity',
                     'computers_laptop_battery_life': 'battery_life',
                     'condition': 'status'}
        # Для хранения данных по обявлению используем датакласс
        laptop = Item(url)
        # Заголовок
        try:
            laptop.title = soup.find('h1', {'class': 'styles_brief_wrapper__title__Ksuxa'}).text
        except Exception as e:
            laptop.title = ''
        # Стоимость
        try:
            price = soup.find('span', class_='styles_main__eFbJH').find('div', class_='styles_discountPrice__WuQiu')
            if not price:
                price = soup.find('span', class_='styles_main__eFbJH')
            laptop.price = float(price.text.replace(' ', '').replace('р.', ''))
        except Exception as e:
            laptop.price = 0
        # Описание
        try:
            laptop.description = soup.find('div', {'itemprop': 'description'}).text
        except Exception as e:
            laptop.description = ''
        # Картинки
        try:
            picture = soup.find_all('img', class_='styles_slide__image__YIPad styles_slide__image__vertical__QdnkQ')
            laptop.picture = list({el['src'] for el in picture})
        except Exception as e:
            laptop.picture = []

        param = soup.find_all('div', class_='styles_parameter_wrapper__L7UfK')
        for el in param:
            try:
                if el.find('div')['data-name'] in pars_list:
                    laptop.__setattr__(pars_list[el.find('div')['data-name']],
                                       el.find('div', class_='styles_parameter_value__BkYDy').find_all(['a', 'span'])[
                                           0].text)
            except Exception as e:
                continue
        return laptop

    @classmethod
    def save_data(cls, data: list[Item]) -> None:
        data = [astuple(i) for i in data]
        cls.DB.update_query("""
        WITH laptop_id as(
        INSERT INTO data_laptops(url, title, price, discription, manufacturer, screen_diagonal,
        screen_resolution, operating_system, processor, ram, video_card_type, video_card, storage_type,
        storage_capacity, battery_life, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO UPDATE SET price = excluded.price RETURNING id)
        INSERT INTO picture_laptops(image, laptop_id)
        VALUES (unnest(COALESCE(%s, ARRAY[]::text[])), (SELECT id FROM laptop_id))
        ON CONFLICT (image) DO NOTHING
        """, data, many=True)

    def runner(self):
        # url страницы с которой начинается парсинг
        url = 'https://www.kufar.by/l/noutbuki'
        flag = True
        while flag:
            links_and_token = self.__get_item_links(self.get_soup(url))
            links = links_and_token[0]
            laptops = []
            for link in tqdm(links, desc='Load data:'):
                soup = self.get_soup(link)
                laptops.append(self.__get_data(soup, link))
            self.save_data(laptops)
            token = links_and_token[1]
            if not token:
                flag = False
            url = f'https://www.kufar.by/l/noutbuki?cursor={token}'


laptot = ParserNotebook()
laptot.runner()
