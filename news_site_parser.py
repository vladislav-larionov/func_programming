""" This class describes abstract class for news site parser """
from abc import ABC, abstractmethod
from datetime import datetime
from bs4 import BeautifulSoup
import requests

headers_req = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0)\
     Gecko/20100101 Firefox/75.0', 'accept': '*/*'
}


class SiteUnreachableException(Exception):
    """ Исключение, описывающее ситуацию, при которой не удаётся подключиться к новостному сайту"""


class NewsSiteParser(ABC):
    """ News site parsers gets information from news sites """

    @abstractmethod
    def parse(self, earliest_date: datetime) -> list:
        """
        Обработка данных новостей взятых с сайта.

        Параметры:
        earliest_date -- дата начала периода, за который необходимо получать новости

        :return: список, включающий в себя информациию о каждой новости
        """

    @staticmethod
    def get_html(website_url):
        """
        Getting html-code of the web-site
        :return: html code
        """

        website_response = requests.get(website_url, headers=headers_req)
        if website_response.status_code != requests.codes.ok:
            raise SiteUnreachableException()
        return BeautifulSoup(website_response.content, 'html.parser')
