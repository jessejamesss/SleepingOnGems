import scrapy
import psycopg2
from itertools import chain
from scrappy.items import PostItem
from scrapy.utils.project import get_project_settings

class PostSpider(scrapy.Spider):
    name = 'posts'
    
    def start_requests(self):
        settings = get_project_settings()
        self.conn = psycopg2.connect(f'host=localhost dbname=sleepingongems user=postgres password={settings.get("DB_PASSWORD")}')
        self.cur = self.conn.cursor()

        self.cur.execute('SELECT * FROM hrefs;')
        hrefs = self.cur.fetchall()

        self.conn.close()
        self.cur.close()

        hrefs = list(chain(*hrefs))
        for href in hrefs:
            yield scrapy.Request(url=href, callback=self.parse)

    def parse(self,response):
        post = PostItem()
        post['caption'] = response.css('h2 ::text').get()
        post['likes'] = response.css('.html-span ::text').get()
        post['date'] = response.css('._aaqe ::attr(title)').get()