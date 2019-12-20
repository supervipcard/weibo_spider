import re
import time
import json
import scrapy
from lxml import etree
from urllib.parse import quote, unquote
from scrapy_redis import spiders
from ..items import *
from ..cookie_pool import CookiePool


class WeiboSpider(spiders.RedisSpider):
    name = 'weibo_master'
    custom_settings = {
        'EXTENSIONS': {
            'project.extensions.ResetCodeExtensions': 0,
            'project.extensions.RestartExtensions': 0,
        }
    }

    def __init__(self, *args, **kwargs):
        super(WeiboSpider, self).__init__(*args, **kwargs)
        self.cookie_pool = CookiePool()

    def make_requests_from_url(self, url):
        url = 'https://d.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=102803_ctg1_1760_-_ctg1_1760&pagebar=0&tab=home&current_page=1&pre_page=1&page=1&pl_name=Pl_Core_NewMixFeed__3&id=102803_ctg1_1760_-_ctg1_1760&script_uri=/&feed_type=1&domain_op=102803_ctg1_1760_-_ctg1_1760&__rnd={}'.format(int(time.time()*1000))
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        return scrapy.Request(url=url, headers=headers, dont_filter=True, callback=self.mblog_parse)

    def mblog_parse(self, response):
        data = json.loads(response.text)['data']
        html = etree.HTML(data)
        elements = html.xpath('//div[@mid]')
        for element in elements:
            mid = element.attrib['mid']

            item = MBlogItem()
            item['mid'] = mid
            item['uid'] = re.search('ouid=(\d+)', element.attrib['tbinfo']).group(1)
            item['url'] = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]//a[@node-type="feed_list_item_date"]/@href')[0]
            item['time'] = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]//a[@node-type="feed_list_item_date"]/@title')[0]
            item['source'] = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]//a[@action-type="app_source"]/text()')

            content = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@node-type="feed_list_content"]')[0]
            item['content'] = content.xpath('./text() | ./a[@class="a_topic"]/text() | ./a[@extra-data="type=atname"]/text() | ./img/@title')
            picture = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@node-type="feed_list_media_prev"]//li[contains(@class, "WB_pic")]//img/@src')
            item['picture'] = ['https:' + re.sub(r'thumb150|orj360', 'mw1024', i) for i in picture]
            video = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@node-type="feed_list_media_prev"]//li[contains(@class, "WB_video")]/@action-data')
            item['video'] = ['https:' + unquote(re.search(r'video_src=(.*?)&', i).group(1)) for i in video if re.search(r'video_src=(.*?)&', i)]

            try:
                item['forward_count'] = element.xpath('.//a[@action-type="fl_forward"]//em[2]/text()')[0]
                item['comment_count'] = element.xpath('.//a[@action-type="fl_comment"]//em[2]/text()')[0]
                item['like_count'] = element.xpath('.//a[@action-type="fl_like"]//em[2]/text()')[0]
            except:
                self.logger.warning('转发评论栏异常，忽略该条微博')
                continue

            if element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@node-type="feed_list_content"]/a[@class="WB_text_opt" and contains(text(), "展开全文")]'):
                yield from self.longtext_request(item)
            else:
                yield item
            official = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@class="WB_info"]/a/i[@title="微博官方认证"]')
            yield from self.user_request(item['uid'], bool(official))
            if '评论' not in element.xpath('.//a[@action-type="fl_comment"]//em[2]/text()')[0]:
                yield from self.comment_request(mid)

    def comment_request(self, mid):
        """只取第一页评论"""
        url = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&id={}&from=singleWeiBo&__rnd=1573536761190'.format(mid)
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        yield scrapy.Request(url=url, headers=headers, meta={'mid': mid}, callback=self.comment_parse)

    def comment_parse(self, response):
        mid = response.meta['mid']

        data = json.loads(response.text)['data']['html']
        html = etree.HTML(data)
        elements = html.xpath('//div[@node-type="root_comment"]')
        for element in elements:
            item = CommentItem()
            item['comment_id'] = element.attrib['comment_id']
            item['mid'] = mid
            uid = element.xpath('./div[@node-type="replywrap"]/div[@class="WB_text"]/a[1]/@usercard')[0]
            item['uid'] = re.search(r'(\d+)', uid).group(1)

            content = element.xpath('./div[@node-type="replywrap"]/div[@class="WB_text"]')[0]
            item['content'] = content.xpath('./text() | ./a[@extra-data="type=atname"]/text() | ./img/@title')
            picture = element.xpath('./div[@node-type="replywrap"]/div[@node-type="comment_media_prev"]//li[contains(@class, "WB_pic")]//img/@src')
            item['picture'] = ['https:' + i for i in picture]

            item['time'] = element.xpath('./div[@node-type="replywrap"]/div[contains(@class, "WB_func")]/div[2]/text()')[0]
            item['like_count'] = element.xpath('./div[@node-type="replywrap"]/div[contains(@class, "WB_func")]/div[1]//a[@action-type="fl_like"]//em[2]/text()')[0]
            yield item
            official = element.xpath('./div[@node-type="replywrap"]/div[@class="WB_text"]/a/i[@title="微博官方认证"]')
            yield from self.user_request(item['uid'], bool(official))

    def user_request(self, uid, official):
        url = 'https://weibo.com/{}'.format(uid) if official else 'https://weibo.com/{}/info'.format(uid)
        yield scrapy.Request(url=url, meta={'uid': uid}, callback=self.user_parse)

    def user_parse(self, response):
        item = UserItem()
        item['uid'] = response.meta['uid']
        item['url'] = 'https://weibo.com/{}'.format(item['uid'])
        item['nickname'] = re.search(r'\$CONFIG\[\'onick\'\]=\'(.*?)\';', response.text).group(1)
        html1_text = re.search(r'<script>FM\.view\(({"ns":"pl\.header\.head\.index".*?})\)</script>', response.text).group(1)
        html1_text = json.loads(html1_text)['html']
        html1 = etree.HTML(html1_text)
        item['headPortrait'] = html1.xpath('//p[@class="photo_wrap"]/img/@src')[0]
        item['membershipGrade'] = html1.xpath('//div[@class="pf_username"]/a[@title="微博会员"]/em/@class')
        item['approveType'] = html1.xpath('//div[@class="pf_photo"]/a/em/@class')
        item['identity'] = html1.xpath('//div[@class="pf_photo"]/a/em/@title')

        match = re.search(r'<script>FM\.view\(({.*?"domid":"Pl_Official_PersonalInfo.*?})\)</script>', response.text)
        if match:
            html2_text = json.loads(match.group(1))['html']
            html2 = etree.HTML(html2_text)
            item['realName'] = html2.xpath('//ul/li/span[text()="真实姓名："]/following-sibling::*[1]/text()')
            item['area'] = html2.xpath('//ul/li/span[text()="所在地："]/following-sibling::*[1]/text()')
            item['sex'] = html2.xpath('//ul/li/span[text()="性别："]/following-sibling::*[1]/text()')
            item['sexualOrientation'] = html2.xpath('//ul/li/span[text()="性取向："]/following-sibling::*[1]/text()')
            item['relationshipStatus'] = html2.xpath('//ul/li/span[text()="感情状况："]/following-sibling::*[1]/text()')
            item['birthday'] = html2.xpath('//ul/li/span[text()="生日："]/following-sibling::*[1]/text()')
            item['bloodType'] = html2.xpath('//ul/li/span[text()="血型："]/following-sibling::*[1]/text()')
            item['blog'] = html2.xpath('//ul/li/span[text()="博客："]/following-sibling::*[1]/text()')
            item['intro'] = html2.xpath('//ul/li/span[text()="简介："]/following-sibling::*[1]/text()')
            item['registrationDate'] = html2.xpath('//ul/li/span[text()="注册时间："]/following-sibling::*[1]/text()')
            item['domainHacks'] = html2.xpath('//ul/li/span[text()="个性域名："]/following-sibling::*[1]/a/text()')
            item['email'] = html2.xpath('//ul/li/span[text()="邮箱："]/following-sibling::*[1]/text()')
            item['qq'] = html2.xpath('//ul/li/span[text()="QQ："]/following-sibling::*[1]/text()')
            item['msn'] = html2.xpath('//ul/li/span[text()="MSN："]/following-sibling::*[1]/text()')

            item['jobInformation'] = []
            job_group = html2.xpath('//ul/li/span[text()="公司："]/following-sibling::*')
            for job in job_group:
                text_list = job.xpath('.//text()')
                text_list = [i.strip() for i in text_list if i.strip()]
                if text_list:
                    job_information = {'company': text_list[0], 'during_time': None, 'area': None, 'position': None}
                    for cell in text_list:
                        if re.search(r'\([\d\s]+-.*?\)', cell):
                            job_information['during_time'] = cell.strip()[1: -1].replace(' ', '')
                        if '地区：' in cell:
                            job_information['area'] = cell.replace('地区：', '').replace('，', '').strip()
                        if '职位：' in cell:
                            job_information['position'] = cell.replace('职位：', '').strip()
                    item['jobInformation'].append(job_information)

            item['educationInformation'] = []
            education_group = html2.xpath('//div[@class="obj_name"]/h2[text()="教育信息"]/parent::div/parent::div/following-sibling::div[1]/div/ul/li')
            for education in education_group:
                school_type = education.xpath('./span[1]/text()')[0].strip()[0: -1]
                education_text = etree.tostring(education, method='html', encoding='utf8').decode('utf8')
                for cell in re.findall(r'<a .*?>(.*?)</a>(.*?)<br>', education_text):
                    school_name = cell[0].strip() if cell[0].strip() else None
                    year = cell[1].strip()[1: -1] if cell[1].strip() else None
                    if school_name:
                        item['educationInformation'].append({'school_type': school_type, 'school_name': school_name, 'year': year})

            item['tabs'] = html2.xpath('//ul/li/span[text()="标签："]/following-sibling::*[1]/a/text()')
            item['tabs'] = [i.strip() for i in item['tabs'] if i.strip()]

        html3_text = re.search(r'<script>FM\.view\(({.*?"domid":"Pl_Core_T8CustomTriColumn.*?,"html":.*?})\)</script>', response.text).group(1)
        html3_text = json.loads(html3_text)['html']
        html3 = etree.HTML(html3_text)
        item['following'] = html3.xpath('//table[@class="tb_counter"]/tbody/tr/td[1]//strong/text()')[0]
        item['followers'] = html3.xpath('//table[@class="tb_counter"]/tbody/tr/td[2]//strong/text()')[0]
        item['mblogNum'] = html3.xpath('//table[@class="tb_counter"]/tbody/tr/td[3]//strong/text()')[0]
        yield item
        if response.meta['depth'] <= 20:
            if int(html3.xpath('//table[@class="tb_counter"]/tbody/tr/td[3]//strong/text()')[0]) > 0:
                yield from self.user_mblog_request(item['uid'])
            # if int(html3.xpath('//table[@class="tb_counter"]/tbody/tr/td[1]//strong/text()')[0]) > 0:
            #     yield from self.user_following_request(item['uid'])
            # if int(html3.xpath('//table[@class="tb_counter"]/tbody/tr/td[2]//strong/text()')[0]) > 0:
            #     yield from self.user_followers_request(item['uid'])

    def user_mblog_request(self, uid):
        url = 'https://weibo.com/{}?is_ori=1'.format(uid)
        yield scrapy.Request(url=url, callback=self.user_mblog_parse)

    def user_mblog_parse(self, response):
        html_text = re.search(r'<script>FM\.view\(({.*?"domid":"Pl_Official_MyProfileFeed__.*?,"html":.*?})\)</script>', response.text).group(1)
        html_text = json.loads(html_text)['html']
        html = etree.HTML(html_text)
        elements = html.xpath('//div[@mid]')
        for element in elements:
            mid = element.attrib['mid']

            item = MBlogItem()
            item['mid'] = mid
            item['uid'] = re.search('ouid=(\d+)', element.attrib['tbinfo']).group(1)
            item['url'] = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]//a[@node-type="feed_list_item_date"]/@href')[0]
            item['url'] = 'https://weibo.com' + item['url'].split('?')[0]
            item['time'] = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]//a[@node-type="feed_list_item_date"]/@title')[0]
            item['source'] = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]//a[@action-type="app_source"]/text()')

            content = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@node-type="feed_list_content"]')[0]
            item['content'] = content.xpath('./text() | ./a[@class="a_topic"]/text() | ./a[@extra-data="type=atname"]/text() | ./img/@title')
            picture = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@node-type="feed_list_media_prev"]//li[contains(@class, "WB_pic")]//img/@src')
            item['picture'] = ['https:' + re.sub(r'thumb150|orj360', 'mw1024', i) for i in picture]
            video = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@node-type="feed_list_media_prev"]//li[contains(@class, "WB_video")]/@action-data')
            item['video'] = ['https:' + unquote(re.search(r'video_src=(.*?)&', i).group(1)) for i in video if re.search(r'video_src=(.*?)&', i)]

            try:
                item['forward_count'] = element.xpath('.//a[@action-type="fl_forward"]//em[2]/text()')[0]
                item['comment_count'] = element.xpath('.//a[@action-type="fl_comment"]//em[2]/text()')[0]
                item['like_count'] = element.xpath('.//a[@action-type="fl_like"]//em[2]/text()')[0]
            except:
                self.logger.warning('转发评论栏异常，忽略该条微博')
                continue

            if element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@node-type="feed_list_content"]/a[@class="WB_text_opt" and contains(text(), "展开全文")]'):
                yield from self.longtext_request(item)
            else:
                yield item
            if '评论' not in element.xpath('.//a[@action-type="fl_comment"]//em[2]/text()')[0]:
                yield from self.comment_request(mid)

    def user_following_request(self, uid):
        url = 'https://weibo.com/{}/follow'.format(uid)
        yield scrapy.Request(url=url, callback=self.user_follow_parse)

    def user_followers_request(self, uid):
        url = 'https://weibo.com/{}/follow?relate=fans'.format(uid)
        yield scrapy.Request(url=url, callback=self.user_follow_parse)

    def user_follow_parse(self, response):
        html_text = re.search(r'<script>FM\.view\(({.*?"domid":"Pl_Official_HisRelation__.*?,"html":.*?})\)</script>', response.text).group(1)
        html_text = json.loads(html_text)['html']
        html = etree.HTML(html_text)
        elements = html.xpath('//ul[@node-type="userListBox"]/li')
        for element in elements:
            match = re.search(r'uid=(\d+)&', element.xpath('./@action-data')[0])
            if match:
                uid = match.group(1)
                official = element.xpath('.//a/i[@title="微博官方认证"]')
                yield from self.user_request(uid, bool(official))

    def longtext_request(self, item):
        url = 'https://d.weibo.com/p/aj/mblog/getlongtext?ajwvr=6&mid={}&is_settop&is_sethot&is_setfanstop&is_setyoudao&__rnd=1573536761190'.format(item['mid'])
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        yield scrapy.Request(url=url, headers=headers, meta={'item': item}, callback=self.longtext_parse)

    def longtext_parse(self, response):
        item = response.meta['item']

        data = json.loads(response.text)['data']
        if data:
            html_text = '<body>' + data['html'] + '</body>'
            html = etree.HTML(html_text)
            item['content'] = html.xpath('body/text() | body/a[@class="a_topic"]/text() | body/a[@extra-data="type=atname"]/text() | body/img/@title')
            yield item
        else:
            self.logger.warning('{} <{}>'.format(json.loads(response.text), response.url))
