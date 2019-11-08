# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MBlogItem(scrapy.Item):
    mid = scrapy.Field()
    uid = scrapy.Field()
    time = scrapy.Field()
    source = scrapy.Field()
    content = scrapy.Field()
    picture = scrapy.Field()
    video = scrapy.Field()
    forward_count = scrapy.Field()
    comment_count = scrapy.Field()
    like_count = scrapy.Field()


class CommentItem(scrapy.Item):
    comment_id = scrapy.Field()
    mid = scrapy.Field()
    uid = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
    like_count = scrapy.Field()


class UserItem(scrapy.Item):
    pass
