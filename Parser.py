import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from pprint import pprint

#URL страницы раздела сайта с которого парсим данные
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

def get_html_page(key_page:str, name_json:str):
    """
    Функция выгрузки HTML кода страницы.
    URL_page : одинаковая часть URL страниц (при пагинации)
    :param key_page: уникальный ключ страницы (при пагинации)
    :param name_json: название Json файла
    :return: сохраняет в каталог JSON HTML код
    """
    response = requests.get(f'{URL_page}{key_page}', headers=HEADERS).text
    soup = BeautifulSoup(response, 'lxml').find('script', id='__NEXT_DATA__').text
    data = json.loads(soup)#['props']['initialState']['listing']['ads']
    with open(f'{name_json}.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))  # Преобразуем полученный код в читабельный вид

# get_html_page('eyJ0IjoicmVsIiwiYyI6W3sibiI6Imxpc3RfdGltZSIsInYiOjE2OTY3MTY5NjEwMDB9LHsibiI6ImFkX2lkIiwidiI6MTg3MDMxMzgzfV0sImYiOnRydWUsInAiOjIzN30%3D', 'test_last')

def get_pages_link(first_page:str):
    list_url=[]
    list_url.append(first_page)
    url_page = first_page
    number_page = 1
    pagination = True
    while pagination:
        response = requests.get(url_page, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'lxml').find('script', id='__NEXT_DATA__').text
        data = json.loads(soup)['props']['initialState']['listing']['pagination']
        number_page += 1

        for el in tqdm(data, desc='list dict'):
            if el['num'] == number_page:
                token = el['token'].replace('=','%3D')
                link_page = f'https://www.kufar.by/l/noutbuki?cursor={token}'
                list_url.append(link_page)
                url_page = link_page
            elif data[len(data) - 1]['num'] < number_page:
                pagination = False

    return list_url

pprint(get_pages_link('https://www.kufar.by/l/noutbuki?cursor=eyJ0IjoiYWJzIiwiZiI6dHJ1ZSwicCI6MX0%3D'))





# def get_flat_data(ad_link: str, parametrs: dict) -> dict:
#     """Функция сбора данных по одному объявлению"""
#     flat = parametrs.copy()
#     code_params = {'item_id': 'ad_id',
#                     'title': 'subject',
#                     'price': 'price_usd',
#                     'picture': 'path',
#                     'discription': '',
#                     'manufacturer': 'computers_laptop_brand',
#                     'screen_diagonal': 'computers_laptop_diagonal',
#                     'screen_resolution': 'computers_laptop_resolution',
#                     'operating_system': 'computers_laptop_os',
#                     'processor': 'computers_laptop_processor',
#                     'ram': 'computer_equipment_laptops_ram',
#                     'video_card_type': 'computers_laptop_videocard',
#                     'video_card': 'computers_laptop_videocard_brand',
#                     'storage_type': 'computers_laptop_hdd_type',
#                     'storage_capacity': 'computers_laptop_hdd_volume',
#                     'battery_life': 'computers_laptop_battery_life',
#                     'status': 'condition'}
#
#     for par in code_params:
#         try:
#             flat[par] = ad_link[code_params[par]]
#         except Exception:
#             flat[par] = ''
#     try:
#         flat['coordinates'] = str(flat['coordinates'][0]) + ', ' + str(flat['coordinates'][1])
#     except Exception:
#         flat['coordinates'] = ''
#     try:
#         flat['picture'] = str(flat['picture'][0])
#     except Exception:
#         flat['picture'] = ''
#     try:
#         flat['phone_number'] = str(flat['phone_number'][0])
#     except Exception:
#         flat['phone_number'] = ''
#     try:
#         for tb in dict_house_type:
#             if tb == flat['type_building']:
#                 flat['type_building'] = dict_house_type[tb]
#     except Exception:
#         flat['type_building'] = ''
#     return flat
#     # for flat in tqdm(flats, desc='Parametr_2'): # поиск параметров Район и микрорайон
#     #         resp = requests.get(f'https://realt.by/sale-flats/object/{flat["flat_id"]}/', headers=HEADERS)
#     #         sou = BeautifulSoup(resp.text, 'lxml')
#     #         par2 = sou.find('section',
#     #                        {'id': 'map', 'class': 'bg-white flex flex-wrap md:p-6 my-4 rounded-md'}).find_all('li',
#     #                                                                                                           class_='relative py-1')
#     #         for par in par2:
#     #             try:
#     #                 key = par.find('span').text
#     #             except Exception as e:
#     #                 key = ''
#     #             if key == 'Район города':
#     #                 flat['district'] = par.find('a').text
#     #             if key == 'Микрорайон':
#     #                 flat['microdistrict'] = par.find('a').text
#     # pprint(flats)

class Laptop():
    def __init__(self):
        pass
