import re
import time
import json
import scrapy
from lxml import etree
from urllib.parse import quote, unquote
from scrapy_redis import spiders
from ..items import *


class WeiboSpider(spiders.RedisSpider):
    name = 'weibo'

    def start_requests(self):
        url = 'https://d.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=102803_ctg1_1760_-_ctg1_1760&pagebar=-1&tab=home&current_page=0&pre_page=1&page=1&pl_name=Pl_Core_NewMixFeed__3&id=102803_ctg1_1760_-_ctg1_1760&script_uri=/&feed_type=1&domain_op=102803_ctg1_1760_-_ctg1_1760&__rnd={}'.format(int(time.time()*1000))
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'wb_view_log_6824826871=1440*9001; wb_view_log_5685522058=1440*9001; YF-V5-G0=bae6287b9457a76192e7de61c8d66c9d; Ugrow-G0=140ad66ad7317901fc818d7fd7743564; _s_tentry=weibo.com; appkey=; Apache=5134369581550.486.1573439433047; SINAGLOBAL=5134369581550.486.1573439433047; ULV=1573439433055:1:1:1:5134369581550.486.1573439433047:; SUB=_2A25wzLfNDeRhGeBG6VYZ8ijEzD2IHXVTu64FrDV8PUNbmtANLWP4kW9NRgnh7h1h1NbvWLlSXW-bkvyG8LdpHu1v; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWsl29zKPAhzBnv9ckgGmDo5JpX5o275NHD95Qc1hzX1hzc1hMpWs4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNSonEShnESonNeBtt; SUHB=0HTh2ChIHD1jBB; ALF=1574044312; SSOLoginState=1573439389; WBtopGlobal_register_version=307744aa77dd5677; cross_origin_proto=SSL; YF-Page-G0=02467fca7cf40a590c28b8459d93fb95|1573440001|1573440001; webim_unReadCount=%7B%22time%22%3A1573440019347%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A3%2C%22msgbox%22%3A0%7D',
        }
        yield scrapy.Request(url=url, headers=headers, callback=self.mblog_parse)

    def mblog_parse(self, response):
        data = json.loads(response.text)['data']
        html = etree.HTML(data)
        elements = html.xpath('//div[@mid]')
        for element in elements:
            mid = element.attrib['mid']

            item = MBlogItem()
            item['mid'] = mid
            item['uid'] = re.search('ouid=(\d+)', element.attrib['tbinfo']).group(1)
            item['time'] = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]//a[@node-type="feed_list_item_date"]/@title')[0]
            item['source'] = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]//a[@action-type="app_source"]/text()')
            item['content'] = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@node-type="feed_list_content"]/text()')

            picture = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@node-type="feed_list_media_prev"]//li[contains(@class, "WB_pic")]//img/@src')
            video = element.xpath('./div[@node-type="feed_content"]/div[@class="WB_detail"]/div[@node-type="feed_list_media_prev"]//li[contains(@class, "WB_video")]/@action-data')
            item['picture'] = ['https:' + i.replace('thumb150', 'mw1024').replace('orj360', 'mw1024') if '.gif' in i else 'https:' + i for i in picture]
            item['video'] = ['https:' + unquote(re.search(r'video_src=(.*?)&', i).group(1)) for i in video]

            item['forward_count'] = element.xpath('.//a[@action-type="fl_forward"]//em[2]/text()')[0]
            item['comment_count'] = element.xpath('.//a[@action-type="fl_comment"]//em[2]/text()')[0]
            item['like_count'] = element.xpath('.//a[@action-type="fl_like"]//em[2]/text()')[0]
            yield item
            href = 'https://weibo.com/{}/info'.format(item['uid'])
            yield from self.user_request(href)
            yield from self.comment_paging(mid, 1)

    def comment_paging(self, mid, page, previous_page_sign=None):
        url = 'https://weibo.com/aj/v6/comment/big'
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'wb_view_log_6824826871=1440*9001; wb_view_log_5685522058=1440*9001; YF-V5-G0=bae6287b9457a76192e7de61c8d66c9d; Ugrow-G0=140ad66ad7317901fc818d7fd7743564; _s_tentry=weibo.com; appkey=; Apache=5134369581550.486.1573439433047; SINAGLOBAL=5134369581550.486.1573439433047; ULV=1573439433055:1:1:1:5134369581550.486.1573439433047:; SUB=_2A25wzLfNDeRhGeBG6VYZ8ijEzD2IHXVTu64FrDV8PUNbmtANLWP4kW9NRgnh7h1h1NbvWLlSXW-bkvyG8LdpHu1v; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWsl29zKPAhzBnv9ckgGmDo5JpX5o275NHD95Qc1hzX1hzc1hMpWs4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNSonEShnESonNeBtt; SUHB=0HTh2ChIHD1jBB; ALF=1574044312; SSOLoginState=1573439389; WBtopGlobal_register_version=307744aa77dd5677; cross_origin_proto=SSL; YF-Page-G0=02467fca7cf40a590c28b8459d93fb95|1573440001|1573440001; webim_unReadCount=%7B%22time%22%3A1573440019347%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A3%2C%22msgbox%22%3A0%7D',
        }
        params = {
            'page': str(page),
            'ajwvr': '6',
            'id': mid,
            'from': 'singleWeiBo',
            '__rnd': str(int(time.time() * 1000))
        }
        yield scrapy.FormRequest(url=url, method='get', headers=headers, formdata=params, meta={'mid': mid, 'page': page, 'previous_page_sign': previous_page_sign}, callback=self.comment_parse)

    def comment_parse(self, response):
        mid = response.meta['mid']
        page = response.meta['page']
        previous_page_sign = response.meta['previous_page_sign']

        data = json.loads(response.text)['data']['html']
        html = etree.HTML(data)
        elements = html.xpath('//div[@node-type="root_comment"]')

        if elements:
            current_page_sign = elements[0].attrib['comment_id']
            if current_page_sign != previous_page_sign:
                for element in elements:
                    item = CommentItem()
                    item['comment_id'] = element.attrib['comment_id']
                    item['mid'] = mid
                    uid = element.xpath('./div[@node-type="replywrap"]/div[@class="WB_text"]/a[1]/@usercard')[0]
                    item['uid'] = re.search(r'(\d+)', uid).group(1)
                    item['content'] = element.xpath('./div[@node-type="replywrap"]/div[@class="WB_text"]/text()')
                    item['time'] = element.xpath('./div[@node-type="replywrap"]/div[contains(@class, "WB_func")]/div[2]/text()')[0]
                    item['like_count'] = element.xpath('./div[@node-type="replywrap"]/div[contains(@class, "WB_func")]/div[1]//a[@action-type="fl_like"]//em[2]/text()')[0]
                    yield item
                    href = 'https:' + element.xpath('./div[@node-type="replywrap"]/div[@class="WB_text"]/a[1]/@href')[0] + '/info'
                    yield from self.user_request(href)
                yield from self.comment_paging(mid, page+1, current_page_sign)

    def user_request(self, url):
        headers = {
            'Cookie': 'wb_view_log_6824826871=1440*9001; wb_view_log_5685522058=1440*9001; YF-V5-G0=bae6287b9457a76192e7de61c8d66c9d; Ugrow-G0=140ad66ad7317901fc818d7fd7743564; _s_tentry=weibo.com; appkey=; Apache=5134369581550.486.1573439433047; SINAGLOBAL=5134369581550.486.1573439433047; ULV=1573439433055:1:1:1:5134369581550.486.1573439433047:; SUB=_2A25wzLfNDeRhGeBG6VYZ8ijEzD2IHXVTu64FrDV8PUNbmtANLWP4kW9NRgnh7h1h1NbvWLlSXW-bkvyG8LdpHu1v; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWsl29zKPAhzBnv9ckgGmDo5JpX5o275NHD95Qc1hzX1hzc1hMpWs4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNSonEShnESonNeBtt; SUHB=0HTh2ChIHD1jBB; ALF=1574044312; SSOLoginState=1573439389; WBtopGlobal_register_version=307744aa77dd5677; cross_origin_proto=SSL; YF-Page-G0=02467fca7cf40a590c28b8459d93fb95|1573440001|1573440001; webim_unReadCount=%7B%22time%22%3A1573440019347%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A3%2C%22msgbox%22%3A0%7D',
        }
        yield scrapy.Request(url=url, headers=headers, meta={'url': url}, callback=self.user_parse)

    def user_parse(self, response):
        item = UserItem()
        item['url'] = response.meta['url']
        item['uid'] = re.search(r'\$CONFIG\[\'oid\'\]=\'(.*?)\';', response.text).group(1)
        item['nickname'] = re.search(r'\$CONFIG\[\'onick\'\]=\'(.*?)\';', response.text).group(1)
        html1_text = re.search(r'<script>FM\.view\(({"ns":"pl\.header\.head\.index".*?})\)</script>', response.text).group(1)
        html1_text = json.loads(html1_text)['html']
        html1 = etree.HTML(html1_text)
        item['headPortrait'] = html1.xpath('//p[@class="photo_wrap"]/img/@src')[0]
        item['membershipGrade'] = html1.xpath('//div[@class="pf_username"]/a[@title="微博会员"]/em/@class')
        item['identity'] = html1.xpath('//div[@class="pf_intro"]/@title')

        html2_text = re.search(r'<script>FM\.view\(({.*?"domid":"Pl_Official_PersonalInfo.*?})\)</script>', response.text).group(1)
        html2_text = json.loads(html2_text)['html']
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

        html3_text = re.search(r'<script>FM\.view\(({.*?"domid":"Pl_Core_T8CustomTriColumn.*?})\)</script>', response.text).group(1)
        html3_text = json.loads(html3_text)['html']
        html3 = etree.HTML(html3_text)
        item['following'] = html3.xpath('//table[@class="tb_counter"]/tbody/tr/td[1]/a/strong/text()')[0]
        item['followers'] = html3.xpath('//table[@class="tb_counter"]/tbody/tr/td[2]/a/strong/text()')[0]
        item['mblogNum'] = html3.xpath('//table[@class="tb_counter"]/tbody/tr/td[3]/a/strong/text()')[0]
        yield item
