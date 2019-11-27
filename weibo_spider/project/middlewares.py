# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import re
import time
import json
import logging
import random
from scrapy import signals
from celery_tasks.tasks import task

logger = logging.getLogger(__name__)


class UserSpecialMiddleware(object):
    def process_response(self, request, response, spider):
        if request.callback.__name__ == 'user_parse':
            if response.status == 302 and response.headers['Location'] == b'https://weibo.com/sorry?pagenotfound&':
                logger.info('特殊用户，更换URL再次请求')
                return request.replace(url=request.url[0: -5])
        return response


class UserErrorMiddleware(object):
    def process_response(self, request, response, spider):
        if request.callback.__name__ == 'user_parse':
            if response.status == 200 and not re.search(r'<script>FM\.view\(({.*?"domid":"Pl_Core_T8CustomTriColumn.*?,"html":.*?})\)</script>', response.text):
                logger.info('用户详情页异常，再次请求')
                request.dont_filter = True
                return request
        return response


class IPErrorMiddleware(object):
    def process_response(self, request, response, spider):
        if response.status == 414:
            logger.info('IP被封禁，暂停30秒')
            time.sleep(30)
            request.dont_filter = True
            return request
        return response


class CookieMiddleware(object):
    def process_request(self, request, spider):
        while True:
            result = spider.cookie_pool.select()
            if result:
                username, password, cookies = result
                request.meta['username'] = username
                request.meta['password'] = password
                if cookies:
                    request.headers['Cookie'] = cookies
                break
            else:
                time.sleep(5)

    def process_response(self, request, response, spider):
        if response.status == 302 and (b'passport.weibo.com/visitor/visitor' in response.headers['Location'] or b'login.sina.com.cn/sso/login.php' in response.headers['Location']):
            logger.warning('登录状态无效：{}'.format(request.meta.get('username')))
            spider.cookie_pool.update_code(request.meta.get('username'), -1)
            task.delay(request.meta.get('username'), request.meta.get('password'))
            request.dont_filter = True
            return request
        return response


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = 'https://xiangchen:pl1996317@101.132.71.2:3129'


class ADSLProxyMiddleware(object):
    def __init__(self, proxy_key):
        self.proxy_key = proxy_key

    @classmethod
    def from_crawler(cls, crawler):
        proxy_key = crawler.settings.get('REDIS_PROXY_KEY')
        return cls(proxy_key)

    def process_request(self, request, spider):
        while True:
            rows = spider.server.hgetall(self.proxy_key)
            if rows:
                proxy = random.choice(list(rows.values())).decode('utf-8')
                request.meta['proxy'] = proxy.replace('http://', 'https://')
                break
            time.sleep(1)


class AccountExceptionMiddleware(object):
    def process_response(self, request, response, spider):
        if request.callback.__name__ == 'mblog_parse':
            if response.status == 200 and '暂时没有内容哦，稍后再来试试吧' in json.loads(response.text)['data']:
                logger.warning('账号异常：{}'.format(request.meta.get('username')))
                spider.cookie_pool.update_code(request.meta.get('username'), -3)
                request.dont_filter = True
                return request
        elif request.callback.__name__ == 'comment_parse':
            if response.status == 200 and json.loads(response.text)['data'] in ['https://weibo.com/sorry?userblock&code=20003', 'https://weibo.com/unfreeze']:
                logger.warning('账号异常：{}'.format(request.meta.get('username')))
                spider.cookie_pool.update_code(request.meta.get('username'), -3)
                request.dont_filter = True
                return request
        elif request.callback.__name__ == 'longtext_parse':
            if response.status == 200 and json.loads(response.text)['data'] == '':
                logger.warning('账号异常：{}'.format(request.meta.get('username')))
                spider.cookie_pool.update_code(request.meta.get('username'), -3)
                request.dont_filter = True
                return request
        return response


class ProjectSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProjectDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
