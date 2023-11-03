# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PostItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    caption = scrapy.Field()
    likes = scrapy.Field()
    date = scrapy.Field()
    # pass
