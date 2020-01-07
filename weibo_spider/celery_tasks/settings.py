import os

MYSQL_HOST = os.environ.get('MYSQL_HOST', '')
MYSQL_PORT = os.environ.get('MYSQL_PORT', 3306)
MYSQL_USER = os.environ.get('MYSQL_USER', '')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'weibo_spider')
MYSQL_CHARSET = os.environ.get('MYSQL_CHARSET', 'utf8mb4')

PROXY_USER = os.environ['PROXY_USER1']
PROXY_PASSWORD = os.environ['PROXY_PASSWORD1']
