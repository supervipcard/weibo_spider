# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class NotFoundHandleMiddleware(object):
    def process_response(self, request, response, spider):
        if request.callback.__name__ == 'user_parse':
            if response.status == 302 and response.headers['Location'] == b'https://weibo.com/sorry?pagenotfound&':
                return request.replace(url=request.url[0: -5])
        return response


class CookieMiddleware(object):
    def process_request(self, request, spider):
        request.headers['Cookie'] = 'SINAGLOBAL=5134369581550.486.1573439433047; wvr=6; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWsl29zKPAhzBnv9ckgGmDo5JpX5KMhUgL.FoqReoBReoqRS022dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMc1hzX1hzc1hMp; ALF=1605056223; SSOLoginState=1573520223; SCF=AsT-rSz3zU4N2ePfqPusiWIQhJFv6Tx05dm4q7qJt9NZhoUHe6FvNauPLGNL29sogIEwncAm3BXknrH92rkNSKw.; SUB=_2A25wznMPDeRhGeBG6VYZ8ijEzD2IHXVTuuPHrDV8PUNbmtAKLXeskW9NRgnh7jjR9jV6Po9qK3_awNeqUa6LoF2Y; SUHB=05i6JyXcw9kShn; YF-V5-G0=99df5c1ecdf13307fb538c7e59e9bc9d; Ugrow-G0=d52660735d1ea4ed313e0beb68c05fc5; _s_tentry=weibo.com; Apache=5432629739683.588.1573520238601; ULV=1573520238649:2:2:2:5432629739683.588.1573520238601:1573439433055; wb_view_log_6824826871=1440*9001; YF-Page-G0=aac25801fada32565f5c5e59c7bd227b|1573525857|1573525714; webim_unReadCount=%7B%22time%22%3A1573526030325%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A3%2C%22msgbox%22%3A0%7D'


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
