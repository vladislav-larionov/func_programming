import sys
import re
from datetime import datetime

from parsers.news_site_parser import NewsSiteParser


class YarnewsNetParser(NewsSiteParser):
    """
    Класс парсера разбирающего сайт https://www.yarnews.net/
    """

    def retrieve_article_text(self, link: str) -> str: # Действие
        """
        Получение статьи и выделение из неё нужного текста.

        Параметры:
        link -- ссылка на новость

        :return: строка с текстом статьи
        """
        full_text = ''
        text_parts = super().get_html(link).find('div', class_="text").find_all('p') # Действие
        for part in text_parts:
            part = part.get_text()
            strong_tag = str(re.search(r'<.strong>', part))
            full_text = full_text + part.replace(strong_tag, ' ').strip() + '\n' # Действие
        return full_text

    def parse_news_items(self, items: list, earliest_date: str) -> list: # Действие
        """
        Получение требуемой информации о новостях из html кода списка новостей с сайта.

        Параметры:
        items -- список элементов типа Tag с данными о каждой новости
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список из словарей с разобранными новостями
        """
        news = []
        for item in items:
            title = item.find('a', class_='news-name').get_text()
            link = "https://www.yarnews.net" + item.find('a', class_='news-name').get('href')
            full_text = self.retrieve_article_text(link) # Действие
            date_time = datetime.strptime(item.find('span', class_="news-date").get_text(), "%d.%m.%Y в %H:%M")
            print(f'{date_time.strftime("%H:%M:%S, %Y-%m-%d")} | {title}', file=sys.stderr) # Действие
            categories = list()
            if date_time > earliest_date:
                news.append({
                    'title': title,
                    'link': link,
                    'full_text': full_text,
                    'date_time': date_time,
                    'categories': categories,
                    'source': 'YarNews'
                })
            else:
                return news, False
        return news, True

    def parse(self, earliest_date: datetime) -> list: # Действие
        """
        Обработка данных новостей взятых с сайта "YarNews".

        Параметры:
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список, включающий в себя информациию о каждой новости
        """
        news = []
        news_loaded = 0
        more_news_exists = True
        while more_news_exists:
            request = super().get_html('https://www.yarnews.net/news/chronicle/ajax/' + str(news_loaded) + '/') # Действие
            items = request.find_all('div', class_="news-feed-info")
            news_from_parser, more_news_exists = self.parse_news_items(items, earliest_date) # Действие
            news = news + news_from_parser
            news_loaded += 30
        return news
