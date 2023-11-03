import time
import scrapy
import psycopg2
from itertools import chain
from scrappy.items import PostItem
from urllib.parse import urlencode
from scrapy.utils.project import get_project_settings

class PostSpider(scrapy.Spider):
    name = 'posts'
    allowed_domains = ['www.instagram.com']

    def start_requests(self):
        settings = get_project_settings()
        head = {
            "authority": "static.cdninstagram.com",
            "method" : "GET",
            "path" : "/btmanifest/1009667778/instagram/main",
            "scheme" : "https",
            "Accept" : "*/*",
            "Accept-Encoding" : "gzip, deflate, br",
            "Accept-Language" : "en-US,en;q=0.9",
            "Cache-Control" : "no-cache",
            "Origin" : "https://instagram.com",
            "Pragma" : "no-cache",
            "Sec-Ch-Ua" : '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            "Sec-Ch-Ua-Mobile" : "?0",
            "Sec-Ch-Ua-Platform" : "macOS",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "cross-site",
            "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        }
  
        self.conn = psycopg2.connect(f'host=localhost dbname=sleepingongems user=postgres password={settings.get("DB_PASSWORD")}')
        self.cur = self.conn.cursor()

        self.cur.execute('SELECT * FROM hrefs;')
        hrefs = self.cur.fetchall()

        self.conn.close()
        self.cur.close()

        hrefs = list(chain(*hrefs))
        for href in hrefs:
            yield scrapy.Request(url=href, callback=self.parse, headers=head)

    def parse(self,response):
        post = PostItem()
        post['caption'] = response.css('h2 ::text').get()
        post['likes'] = response.css('.html-span ::text').get()
        post['date'] = response.css('._aaqe ::attr(title)').get()

        yield post