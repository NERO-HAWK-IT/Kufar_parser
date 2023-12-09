import requests
from bs4 import BeautifulSoup


class ParserNotebook:
    # Данные для авторизации на сайте
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'}

    @classmethod
    def get_soup(cls, url: str) -> BeautifulSoup:
        response = requests.get(url, headers=cls.HEADERS)
        print(f'{response.status_code}' | {url})
        soup = BeautifulSoup(response.text, 'lxml')
        return soup

    def get_page_links(self, soup: BeautifulSoup):

    @staticmethod
    def get_item_links(self, soup: BeautifulSoup) -> list:
        links = soup.find_all('a', {'class': 'styles_wrapper__5FoK7', 'data-testid': True})
        links = [el["href"].split('?')[0] for el in links]
        return links

    def get_data(self, soup: BeautifulSoup) -> None:
        title = soup.find('h1', {'class':'styles_brief_wrapper__title__Ksuxa'})
        if title:
            title = title.text
