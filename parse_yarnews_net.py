class YarnewsNetParser(NewsSiteParser):

    def parse(self, earliest_date: datetime) -> list: # Действие
        news = []
        news_loaded = 0
        more_news_exists = True
        while more_news_exists:
            page_body = super().get_html(self.generate_articles_url(news_loaded))
            items = page_body.find_all('div', class_="news-feed-info")
            news_from_parser, more_news_exists = self.parse_news_items(items, earliest_date)
            news = news + news_from_parser
            news_loaded += 30
        return news

    def generate_articles_url(self, loaded) -> str:  # Вычисление
        return 'https://www.yarnews.net/news/chronicle/ajax/' + str(loaded) + '/'

    def parse_news_items(self, items: list, earliest_date: str) -> list: # Действие
        news = []
        for item in items:
            link = self.extract_article_url(item)
            article_body = super().get_html(link)
            article = self.parse_article(article_body, link)
            self.log_article_parsed_msg(article)
            if self.article_is_suitable(article, earliest_date):
                news.append(article)
            else:
                return news, False
        return news, True

    def extract_article_url(self, article_tag) -> str:  # Вычисление
        return "https://www.yarnews.net" + article_tag.find('a', class_='news-name').get('href')

    def parse_article(self, article_tag, link) -> dict: # Вычисление
        title = article_tag.find('h1').get_text()
        full_text = self.retrieve_article_text(article_tag)
        date_time = datetime.strptime(article_tag.find('span', class_="news-date").get_text(), "%d.%m.%Y в %H:%M")
        return self.create_article(title, link, full_text, date_time)

    def retrieve_article_text(self, article_body: Tag) -> str:  # Вычисление
        full_text = ''
        text_parts = article_body.find('div', class_="text").find_all('p')
        for part in text_parts:
            part_text = part.get_text()
            strong_tag = str(re.search(r'<.strong>', part_text))
            full_text = full_text + part_text.replace(strong_tag, ' ').strip() + '\n'
        return full_text

    def create_article(self, title, link, full_text, date_time) -> dict:  # Вычисление
        return {'title': title, 'link': link, 'full_text': full_text, 'date_time': date_time, 'categories': list(), 'source': 'YarNews'}

    def log_article_parsed_msg(self, article): # Действие
        print(f'{date_time.strftime("%H:%M:%S, %Y-%m-%d")} | {article['title']}', file=sys.stderr) # Действие

    def article_is_suitable(self, article, earliest_date) -> bool:  # Вычисление
        return article['date_time'] > earliest_date
