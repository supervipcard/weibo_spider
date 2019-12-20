# -*- coding: utf-8 -*-

# Define here the models for your scraped Extensions

from scrapy.exceptions import NotConfigured
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


class RestartExtensions(object):
    def __init__(self, crawler, idle_number, queue_key):
        self.crawler = crawler
        self.idle_number = idle_number
        self.queue_key = queue_key
        self.idle_count = 0

    @classmethod
    def from_crawler(cls, crawler):
        idle_number = crawler.settings.getint('IDLE_NUMBER', 360)
        queue_key = crawler.settings.get('SCHEDULER_QUEUE_KEY')
        if not queue_key:
            raise NotConfigured
        o = cls(crawler, idle_number, queue_key)
        crawler.signals.connect(o.spider_idle, signal=signals.spider_idle)
        return o

    def spider_idle(self, spider):
        # 当spider进入空闲状态时会调用这个方法一次，之后每隔5秒再调用一次
        # 当持续半个小时都没有spider.redis_key，就关闭爬虫
        # 判断是否存在 redis_key
        if not spider.server.exists(self.queue_key):
            self.idle_count += 1
        else:
            self.idle_count = 0

        if self.idle_count > self.idle_number:
            spider.server.rpush(spider.redis_key, '1')
            self.idle_count = 0
