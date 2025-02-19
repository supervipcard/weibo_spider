# -*- coding: utf-8 -*-

# Scrapy settings for project project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os

BOT_NAME = 'project'

SPIDER_MODULES = ['project.spiders']
NEWSPIDER_MODULE = 'project.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'project.middlewares.ProjectSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'project.middlewares.ABYProxyMiddleware': 110,
    'project.middlewares.UserPageExceptionMiddleware2': 120,
    'project.middlewares.AccountExceptionMiddleware': 150,
    'project.middlewares.UserPageExceptionMiddleware1': 650,
    'project.middlewares.CookieMiddleware': 660,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'project.pipelines.DataCheckPipeline': 300,
    'project.pipelines.SqlPipeline': 400,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

DNSCACHE_ENABLED = True
DNSCACHE_SIZE = 1000
DNS_TIMEOUT = 60

REDIS_HOST = os.environ.get('REDIS_HOST', '')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_PARAMS = {
    'password': os.environ.get('REDIS_PASSWORD', ''),
    'db': os.environ.get('REDIS_DB', 0)
}
REDIS_PROXY_KEY = 'adsl'

DOWNLOAD_TIMEOUT = 10

RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 414]

SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'

# DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
DUPEFILTER_CLASS = "project.bloomfilter.CustomRFPDupeFilter"
DUPEFILTER_DEBUG = True

SCHEDULER_QUEUE_KEY = 'weibo:requests'
SCHEDULER_DUPEFILTER_KEY = 'weibo:dupefilter'

DEPTH_PRIORITY = 1    # 广度优先

SCHEDULER_PERSIST = True    # 是否在关闭时保留原来的调度器和去重记录
SCHEDULER_FLUSH_ON_START = False    # 是否在开始之前清空调度器和去重记录

BLOOMFILTER_BIT = 30
BLOOMFILTER_HASH_NUMBER = 6

MYSQL_HOST = os.environ.get('MYSQL_HOST', '')
MYSQL_PORT = os.environ.get('MYSQL_PORT', 3306)
MYSQL_USER = os.environ.get('MYSQL_USER', '')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'weibo_spider')
MYSQL_CHARSET = os.environ.get('MYSQL_CHARSET', 'utf8mb4')

MYSQL_KEY = "mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset={charset}".format(
    user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOST, port=MYSQL_PORT, db=MYSQL_DB, charset=MYSQL_CHARSET)

MYSQL_POOL_SIZE = 5
MYSQL_POOL_RECYCLE = 7200    # 连接池中的空闲连接超过1小时自动释放。
MYSQL_POOL_TIMEOUT = 30

# REDIRECT_ENABLED = False
# HTTPERROR_ALLOWED_CODES = [302]

# LOG_FILE = ''
LOG_LEVEL = 'INFO'

PROXY_ACCOUNT_LIST = [
    {'username': os.environ['PROXY_USER1'], 'password': os.environ['PROXY_PASSWORD1']},
    {'username': os.environ['PROXY_USER2'], 'password': os.environ['PROXY_PASSWORD2']},
]

RESET_CODE_INTERVAL = 3600

IDLE_NUMBER = int(60 * 0.5 / 5)
