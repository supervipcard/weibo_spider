import requests
from retrying import retry
from ..settings import *


class Request:
    base_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = self.base_headers
        # self.session.proxies = self.get_proxies()

    @staticmethod
    def get_proxies():
        proxyMeta = "http://{user}:{password}@http-dyn.abuyun.com:9020".format(user=PROXY_USER, password=PROXY_PASSWORD)
        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        return proxies

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def get(self, url, **kwargs):
        response = self.session.get(url=url, timeout=10, **kwargs)
        if response.status_code == 200:
            return response
        else:
            raise ConnectionError

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def post(self, url, **kwargs):
        response = self.session.post(url=url, timeout=10, **kwargs)
        if response.status_code == 200:
            return response
        else:
            raise ConnectionError
