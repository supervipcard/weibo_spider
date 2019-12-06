import time
import json
import execjs
import base64
from retrying import retry
from .request import Request
from .cnn.client import Caller


class AccountLogin:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.req = Request()

        with open('celery_tasks/login_task/rsa.js', 'r', encoding='utf-8') as f:
            source = f.read()
        external_runtime = execjs.get()
        self.context = external_runtime.compile(source)

        self.caller = Caller()

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def process(self):
        login_result = self.login(self.prelogin())
        if login_result['retcode'] == '0':
            second_login_result = self.second_login(login_result['ticket'])
            if second_login_result['result'] is True:
                return self.req.session.cookies
            else:
                raise Exception('二次登录失败')
        else:
            raise Exception(login_result['reason'])

    def test(self):
        url = 'https://d.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=102803_ctg1_1760_-_ctg1_1760&pagebar=-1&tab=home&current_page=0&pre_page=1&page=1&pl_name=Pl_Core_NewMixFeed__3&id=102803_ctg1_1760_-_ctg1_1760&script_uri=/&feed_type=1&domain_op=102803_ctg1_1760_-_ctg1_1760&__rnd={}'.format(int(time.time()*1000))
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = self.req.get(url=url, headers=headers)
        response.encoding = 'gbk'

    def prelogin(self):
        """预登录"""
        url = 'https://login.sina.com.cn/sso/prelogin.php'
        params = {
            'entry': 'weibo',
            'su': base64.b64encode(self.username.encode('utf8')),
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.19)',
        }
        response = self.req.get(url=url, params=params)
        return json.loads(response.text)

    def get_code_image(self, pcid):
        """获取验证码图片"""
        url = 'https://login.sina.com.cn/cgi/pin.php?p={}'.format(pcid)
        response = self.req.get(url=url)
        # with open('a.jpg', 'wb') as f:
        #     f.write(response.content)
        return self.caller.run(response.content)

    def login(self, prelogin_result):
        """登录"""
        servertime = prelogin_result['servertime']
        pcid = prelogin_result['pcid']
        nonce = prelogin_result['nonce']
        pubkey = prelogin_result['pubkey']
        rsakv = prelogin_result['rsakv']

        door = self.get_code_image(pcid)
        # door = input('请输入:')
        print(door)

        sp = self.context.call('f1', pubkey, servertime, nonce, self.password)

        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pagerefer': '',
            'pcid': pcid,
            'door': door,
            'vsnf': '1',
            'su': base64.b64encode(self.username.encode('utf8')),
            'service': 'miniblog',
            'servertime': servertime + 100,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': sp,
            'sr': '1440*900',
            'encoding': 'UTF-8',
            'cdult': '2',
            'domain': 'weibo.com',
            'prelt': '48',
            'returntype': 'TEXT',
        }
        response = self.req.post(url=url, data=data)
        return json.loads(response.text)

    def second_login(self, ticket):
        """登录之后的Cookie不全，请求另一个登录接口补全Cookie"""
        url = 'https://passport.weibo.com/wbsso/login'
        params = {
            'ticket': ticket,
            'client': 'ssologin.js(v1.4.19)',
        }
        response = self.req.get(url=url, params=params)
        return json.loads(response.text.strip()[1: -2])

    def check(self):
        url = 'https://weibo.com'
        response = self.req.get(url=url)
        response.encoding = 'utf8'
        return response.text

    def check1(self):
        url = 'https://d.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=102803_ctg1_1760_-_ctg1_1760&pagebar=0&tab=home&current_page=1&pre_page=1&page=1&pl_name=Pl_Core_NewMixFeed__3&id=102803_ctg1_1760_-_ctg1_1760&script_uri=/&feed_type=1&domain_op=102803_ctg1_1760_-_ctg1_1760&__rnd={}'.format(int(time.time()*1000))
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = self.req.get(url=url, headers=headers)
        return json.loads(response.text)

    def check2(self):
        url = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&id=4445537426391409&from=singleWeiBo&__rnd=1573536761190'
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = self.req.get(url=url, headers=headers)
        return json.loads(response.text)

    def check3(self):
        url = 'https://d.weibo.com/p/aj/mblog/getlongtext?ajwvr=6&mid=4445537426391409&is_settop&is_sethot&is_setfanstop&is_setyoudao&__rnd=1573536761190'
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = self.req.get(url=url, headers=headers)
        return json.loads(response.text)

    def check4(self):
        url = 'https://weibo.com/2656274875'
        response = self.req.get(url=url)
        return response.text

    def check5(self):
        url = 'https://weibo.com/1192336151/info'
        response = self.req.get(url=url)
        return response.text

    def check6(self):
        url = 'https://weibo.com/1192336151?is_ori=1'
        response = self.req.get(url=url)
        return response.text
