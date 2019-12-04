# -*- coding: utf-8 -*-

# Define here the models for your scraped Extensions

from twisted.internet import task
from scrapy import signals


class ResetCodeExtensions(object):
    def __init__(self, crawler, interval):
        self.crawler = crawler
        self.interval = interval
        self.task = None

    @classmethod
    def from_crawler(cls, crawler):
        interval = crawler.settings.getint('RESET_CODE_INTERVAL', 3600)
        o = cls(crawler, interval)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.task = task.LoopingCall(self.reset_code, spider)
        self.task.start(self.interval)

    def reset_code(self, spider):
        spider.cookie_pool.reset_code()

    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()
