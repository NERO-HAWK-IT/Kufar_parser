import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from pprint import pprint

# URL страницы раздела сайта с которого парсим данные
URL = 'https://www.kufar.by/l/noutbuki?'

# URL страницы сайта с которого парсим данные
URL_page = 'https://www.kufar.by/l/noutbuki?cursor='

# Данные для авторизации на сайте
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}

# Словарь запрашиваемых параметров квартир с типом значений
Item_parameters = {'item_id': 'INTEGER unique',
                   'title': 'TEXT',
                   'price': 'INTEGER',
                   'picture': 'TEXT',
                   'discription': 'TEXT',
                   'manufacturer': 'TEXT',
                   'screen_diagonal': 'TEXT',
                   'screen_resolution': 'TEXT',
                   'operating_system': 'TEXT',
                   'processor': 'TEXT',
                   'ram': 'INTEGER',
                   'video_card_type': 'TEXT',
                   'video_card': 'TEXT',
                   'storage_type': 'TEXT',
                   'storage_capacity': 'INTEGER',
                   'battery_life': 'INTEGER',
                   'status': 'TEXT'
                   }

# Задаем уникальный параметр
unique_parametr = 'item_id'


def get_html_page(key_page: str, name_json: str):
    """
    Функция выгрузки HTML кода страницы.
    URL_page : одинаковая часть URL страниц (при пагинации)
    :param key_page: уникальный ключ страницы (при пагинации)
    :param name_json: название Json файла
    :return: сохраняет в каталог JSON HTML код
    """
    response = requests.get(f'{URL_page}{key_page}', headers=HEADERS).text
    soup = BeautifulSoup(response, 'lxml').find('script', id='__NEXT_DATA__').text
    data = json.loads(soup)  # ['props']['initialState']['listing']['ads']
    with open(f'{name_json}.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))  # Преобразуем полученный код в читабельный вид


# get_html_page('eyJ0IjoiYWJzIiwiZiI6dHJ1ZSwicCI6MX0%3D', 'page')
#
def get_pages_link(first_page: str) -> list:
    list_url = []
    list_url.append(first_page)
    url_page = first_page
    number_page = 1
    pagination = True
    while pagination:
        response = requests.get(url_page, headers=HEADERS)
        print(response.status_code)
        soup = BeautifulSoup(response.text, 'lxml').find('script', id='__NEXT_DATA__').text
        data = json.loads(soup)['props']['initialState']['listing']['pagination']
        number_page += 1

        for el in tqdm(data, desc='list dict'):
            if el['num'] == number_page:
                token = el['token'].replace('=', '%3D')
                link_page = f'https://www.kufar.by/l/noutbuki?cursor={token}'
                list_url.append(link_page)
                url_page = link_page
            elif data[len(data) - 1]['num'] < number_page:
                pagination = False
    return list_url


def get_items_links(list_url: list) -> list:
    item_url = []
    for page in tqdm(list_url, desc='Parsing items url'):
        responce = requests.get(page, headers=HEADERS)
        soup = BeautifulSoup(responce.text, 'lxml')
        link = soup.find_all('a', {'class': 'styles_wrapper__5FoK7', 'data-testid': True})

        urls = [el["href"].split('?')[0] for el in link if
                el.find('span').text.replace(' ', '').replace('р.', '').isdigit()]
        pprint(urls)
        item_url.extend(urls)
    return item_url


# get_items_links(['https://www.kufar.by/l/noutbuki?cursor=eyJ0IjoiYWJzIiwiZiI6dHJ1ZSwicCI6MX0%3D'])

def get_items_data(item_url: list):
    items = []
    for link in tqdm(item_url, desc='Parsing items data'):
        response = requests.get(link, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'lxml')
        # item_id =link.split('/')[4].split('?')[0]
        # print(item_id)
        pars_list = {'title': ['h1', {'class': 'styles_brief_wrapper__title__Ksuxa'}],
                     'price': ['span', {'class': 'styles_main__eFbJH'}],
                     'picture': ['', {'': ''}],
                     'discription': ['div', {'itemprop': 'description'}],
                     'manufacturer': ['', {'': ''}],
                     'screen_diagonal': ['', {'': ''}],
                     'screen_resolution': ['', {'': ''}],
                     'operating_system': ['', {'': ''}],
                     'processor': ['', {'': ''}],
                     'ram': ['', {'': ''}],
                     'video_card_type': ['', {'': ''}],
                     'video_card': ['', {'': ''}],
                     'storage_type': ['', {'': ''}],
                     'storage_capacity': ['', {'': ''}],
                     'battery_life': ['', {'': ''}],
                     'status': ['', {'': ''}]}
        # for el in pars_list:
        #     try:
        #         print((soup.find(pars_list[el][0], pars_list[el][1])).text)
        #     except:
        #         print('not')

        # try:
        #     param = soup.find('div', class_='styles_parameter_value__BkYDy').text
        # except:
        #     param = ''
        # print(param)
        # raw_params = soup.find_all('div',class_='styles_parameter_block__QBI2S undefined')
        # pprint(raw_params)
        # for par in raw_params:
        #
        #     key = par.find('div', class_='styles_parameter_label__i_OkS').text
        #     value = par.find('a').text
        #     print(key)
        #     print(value)

        # try:
        #     price = soup.find('span', class_='styles_main__eFbJH').text.replace(' ','').replace('р.','')
        # except:
        #     price = ''
        # print(price)
        # try: #возвращает список ссылок на картинки
        #     picture = soup.find_all('img', class_='styles_slide__image__YIPad styles_slide__image__vertical__QdnkQ')
        #     picture = [el['src'] for el in picture]
        # except:
        #     picture = ''
        # print(picture)
        pars_list = {'computers_laptop_brand': 'manufacturer',
                     'computers_laptop_diagonal': 'screen_diagonal',
                     'computers_laptop_resolution': 'screen_resolution',
                     'computers_laptop_os Windows': 'operating_system',
                     'computers_laptop_processor': 'processor',
                     'computer_equipment_laptops_ram': 'ram',
                     'computers_laptop_videocard': 'video_card_type',
                     'computers_laptop_videocard_brand': 'video_card',
                     'computers_laptop_hdd_type': 'storage_type',
                     'computers_laptop_hdd_volume': 'storage_capacity',
                     'computers_laptop_battery_life': 'battery_life',
                     'condition': 'status'}


        a = soup.find_all('div', class_='styles_parameter_wrapper__L7UfK')
        for el in a:
            try:
                if el.find('div')['data-name'] in pars_list:
                    print((pars_list[el.find('div')['data-name']],
                                       el.find('div', class_='styles_parameter_value__BkYDy').find_all(['a', 'span'])[
                                           0].text))
                    # m = el.find('div', class_='styles_parameter_value__BkYDy').find_all(['a','span'])[0].text
                    # print(el.find('div')['data-name'],m)
            except:
                print(None)



get_items_data(['https://www.kufar.by/item/217362762'])


def run_parser():
    pagination = get_pages_link('https://www.kufar.by/l/noutbuki?cursor=eyJ0IjoiYWJzIiwiZiI6dHJ1ZSwicCI6MX0%3D')
    item_links = get_items_links(pagination)
    pprint(item_links)
    print(len(item_links))
    li = []
    [li.append(x) for x in item_links if x not in li]
    print(len(li))


# run_parser()

class Laptop():
    def __init__(self):
        pass
