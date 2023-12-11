import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import models
import DB_client
from pprint import pprint


class ParserNotebook:
    # Данные для авторизации на сайте
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}

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

    def get_page_links(self, url_first_page: str):
        """
        Функция сбора ссылок страниц.
        :param url_first_page: url первой страницы
        :return: возвращает список ссылок страниц
        """
        list_urls = []
        list_urls.append(url_first_page)
        url_page = url_first_page
        number_page = 1
        pagination = True
        while pagination:
            soup = self.get_soup(url_page).find('script', id='__NEXT_DATA__').text
            data = json.loads(soup)['props']['initialState']['listing']['pagination']
            number_page += 1

            for el in tqdm(data, desc='list dict'):
                if el['num'] == number_page:
                    token = el['token'].replace('=', '%3D')
                    link_page = f'https://www.kufar.by/l/noutbuki?cursor={token}'
                    list_urls.append(link_page)
                    url_page = link_page
                elif data[len(data) - 1]['num'] < number_page:
                    pagination = False
        return list_urls

    @staticmethod
    def get_item_links(soup: BeautifulSoup) -> list:
        """
        Функция сбора ссылок объявлений с каждой страницы раздела
        :param soup: BeautifulSoup страницы раздела
        :return: возвращает список urls объявлений
        """
        links = soup.find_all('a', {'class': 'styles_wrapper__5FoK7', 'data-testid': True})
        # далее выбираем ссылки тех объявлений у которых есть стоимость.
        # (span - тег поля стоимости, href атрибут забираем сслыку)
        links = [el["href"].split('?')[0] for el in links if
                 el.find('span').text.replace(' ', '').replace('р.', '').isdigit()]
        return links

    def get_data(self, soup: BeautifulSoup) -> tuple:
        """
        Функция сбора данный по объявлениям
        :param soup: BeautifulSoup страницы объявления
        :return: возвращает кортеж с данными
        """
        # Задаем параметрический словарь где ключь это data-name исз кода страницы, а значение это название переменной
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

        advert = models.Item()
        try:
            advert.title = soup.find('h1', {'class': 'styles_brief_wrapper__title__Ksuxa'}).text
        except:
            advert.title = ''

        try:
            advert.price = int(
                soup.find('span', {'class': 'styles_main__eFbJH'}).text.replace(' ', '').replace('р.', ''))
        except:
            advert.price = 0

        try:
            advert.discription = soup.find('div', {'itemprop': 'description'})
        except:
            advert.discription = ''

        try:
            picture = soup.find_all('img', class_='styles_slide__image__YIPad styles_slide__image__vertical__QdnkQ')
            advert.picture = [el['src'] for el in picture]
        except:
            advert.picture = []

        param = soup.find_all('div', class_='styles_parameter_wrapper__L7UfK')
        for el in param:
            try:
                if el.find('div')['data-name'] in pars_list:
                    advert.__setattr__(pars_list[el.find('div')['data-name']],
                                       el.find('div', class_='styles_parameter_value__BkYDy').find_all(['a', 'span'])[
                                           0].text)
            except:
                continue
        return models.astuple(advert)

    def runner(self, start_url):
        # start_url задается в день парсинга, т.к. cursor динамичный и изменяется ежедневно
        links = self.get_page_links(start_url)

        # Задаем список для сохранения данных
        data_items = list

        # Собираем сслыки всех объявлений
        for link in tqdm(links, desc='Load item links:'):
            soup = self.get_soup(link)
            item_page_links = self.get_item_links(soup)
            # Собираем данные с объявлений и записываем их в список
            for item_link in tqdm(item_page_links, desc='Load data:'):
                soup_item_page = self.get_soup(item_link)
                item_data = self.get_data(soup_item_page)
                data_items.append(item_data) # проанализировать, есть смысл построчно грузить в БД!!!
