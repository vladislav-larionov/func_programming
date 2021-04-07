import sys
import re
from datetime import datetime

from parsers.news_site_parser import NewsSiteParser


class YarnewsNetParser(NewsSiteParser):
    """
    Класс парсера разбирающего сайт https://www.yarnews.net/
    """

    def retrieve_article_text(self, article_body: Tag) -> str: # Вычисление
        """
        Получение статьи и выделение из неё нужного текста.

        Параметры:
        link -- ссылка на новость

        :return: строка с текстом статьи
        """
        full_text = ''
        text_parts = article_body.find('div', class_="text").find_all('p')
        for part in text_parts:
            part = part.get_text()
            strong_tag = str(re.search(r'<.strong>', part))
            full_text = full_text + part.replace(strong_tag, ' ').strip() + '\n'
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
            article = self.parse_article(item)  # Действие
            self.log_article_parsed_msg(article)
            if article['date_time'] > earliest_date:
                news.append(article)
            else:
                return news, False
        return news, True

    def parse_article(self, article_tag) -> dict: # Действие
        title = article_tag.find('a', class_='news-name').get_text()
        link = self.extract_article_url(article_tag)
        article_body =  super().get_html(link) # Действие
        full_text = self.retrieve_article_text(article_body)
        date_time = datetime.strptime(article_tag.find('span', class_="news-date").get_text(), "%d.%m.%Y в %H:%M") # Действие
        categories = list()
        return self.create_article(title, link, full_text, date_time, categories)

    def create_article(self, title, link, full_text, date_time, categories) -> dict:  # Вычисление
        return {
            'title': title,
            'link': link,
            'full_text': full_text,
            'date_time': date_time,
            'categories': categories,
            'source': 'YarNews'
        }

    def log_article_parsed_msg(self, article): # Действие
        print(f'{date_time.strftime("%H:%M:%S, %Y-%m-%d")} | {article['title']}', file=sys.stderr) # Действие

    def extract_article_url(self, article_tag) -> str:  # Вычисление
        return "https://www.yarnews.net" + article_tag.find('a', class_='news-name').get('href')

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
            request = super().get_html(self.generate_articles_url(news_loaded)) # Действие
            items = request.find_all('div', class_="news-feed-info")
            news_from_parser, more_news_exists = self.parse_news_items(items, earliest_date) # Действие
            news = news + news_from_parser
            news_loaded += 30
        return news

    def generate_articles_url(self, loaded) -> str:  # Вычисление
        return 'https://www.yarnews.net/news/chronicle/ajax/' + str(loaded) + '/'