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
            'Cookie': 'SINAGLOBAL=165605077937.38522.1559631746697; un=15058716965; _s_tentry=login.sina.com.cn; Apache=3900361911456.74.1573174984678; ULV=1573174984729:30:4:3:3900361911456.74.1573174984678:1573119308336; wb_view_log_5685522058=1440*9001; login_sid_t=d8646e5095f93f3a4a03d696c20a8b4a; cross_origin_proto=SSL; UOR=,,login.sina.com.cn; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWHn3dd6RIP37HjXOJgJAZK5JpX5K2hUgL.Fo-c1h-feoz7SKn2dJLoIX5LxKnL1h2LB.BLxK.L1-zLBKnLxKnL1h2LBoz_i--ci-zNiKnfi--ci-zNiKnfi--NiKn7iKL2i--NiKn7iKL2; ALF=1604711067; SSOLoginState=1573175067; SCF=ArQGaPR_6L0mQm1eXmMK2OBLY-EAztaBUkFq8nyNzYYccZWbEBGDqJ2QdJFJW6wEu5bXjLBHmId5Xech4ciNeq0.; SUB=_2A25wwM9MDeRhGeNI41cU8izMzjSIHXVTt6eErDV8PUNbmtAfLUqlkW9NSDGoVVtSv4ul3btnEY6t88Pa7juW7hMO; SUHB=08J7Pw-Yc0StGK; wvr=6; YF-Page-G0=bd9e74eeae022c6566619f45b931d426|1573175857|1573175857; webim_unReadCount=%7B%22time%22%3A1573176212949%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A36%2C%22msgbox%22%3A0%7D',
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
            yield from self.comment_paging(mid, 1)

    def comment_paging(self, mid, page, previous_page_sign=None):
        url = 'https://weibo.com/aj/v6/comment/big'
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'SINAGLOBAL=165605077937.38522.1559631746697; un=15058716965; _s_tentry=login.sina.com.cn; Apache=3900361911456.74.1573174984678; ULV=1573174984729:30:4:3:3900361911456.74.1573174984678:1573119308336; wb_view_log_5685522058=1440*9001; login_sid_t=d8646e5095f93f3a4a03d696c20a8b4a; cross_origin_proto=SSL; UOR=,,login.sina.com.cn; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWHn3dd6RIP37HjXOJgJAZK5JpX5K2hUgL.Fo-c1h-feoz7SKn2dJLoIX5LxKnL1h2LB.BLxK.L1-zLBKnLxKnL1h2LBoz_i--ci-zNiKnfi--ci-zNiKnfi--NiKn7iKL2i--NiKn7iKL2; ALF=1604711067; SSOLoginState=1573175067; SCF=ArQGaPR_6L0mQm1eXmMK2OBLY-EAztaBUkFq8nyNzYYccZWbEBGDqJ2QdJFJW6wEu5bXjLBHmId5Xech4ciNeq0.; SUB=_2A25wwM9MDeRhGeNI41cU8izMzjSIHXVTt6eErDV8PUNbmtAfLUqlkW9NSDGoVVtSv4ul3btnEY6t88Pa7juW7hMO; SUHB=08J7Pw-Yc0StGK; wvr=6; YF-Page-G0=bd9e74eeae022c6566619f45b931d426|1573175857|1573175857; webim_unReadCount=%7B%22time%22%3A1573176212949%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A36%2C%22msgbox%22%3A0%7D',
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
            'Cookie': 'SINAGLOBAL=165605077937.38522.1559631746697; un=15058716965; _s_tentry=login.sina.com.cn; Apache=3900361911456.74.1573174984678; ULV=1573174984729:30:4:3:3900361911456.74.1573174984678:1573119308336; wb_view_log_5685522058=1440*9001; login_sid_t=d8646e5095f93f3a4a03d696c20a8b4a; cross_origin_proto=SSL; UOR=,,login.sina.com.cn; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWHn3dd6RIP37HjXOJgJAZK5JpX5K2hUgL.Fo-c1h-feoz7SKn2dJLoIX5LxKnL1h2LB.BLxK.L1-zLBKnLxKnL1h2LBoz_i--ci-zNiKnfi--ci-zNiKnfi--NiKn7iKL2i--NiKn7iKL2; ALF=1604711067; SSOLoginState=1573175067; SCF=ArQGaPR_6L0mQm1eXmMK2OBLY-EAztaBUkFq8nyNzYYccZWbEBGDqJ2QdJFJW6wEu5bXjLBHmId5Xech4ciNeq0.; SUB=_2A25wwM9MDeRhGeNI41cU8izMzjSIHXVTt6eErDV8PUNbmtAfLUqlkW9NSDGoVVtSv4ul3btnEY6t88Pa7juW7hMO; SUHB=08J7Pw-Yc0StGK; wvr=6; YF-Page-G0=bd9e74eeae022c6566619f45b931d426|1573175857|1573175857; webim_unReadCount=%7B%22time%22%3A1573176212949%2C%22dm_pub_total%22%3A0%2C%22chat_group_client%22%3A0%2C%22allcountNum%22%3A36%2C%22msgbox%22%3A0%7D',
        }
        yield scrapy.Request(url=url, headers=headers, callback=self.user_parse)

    def user_parse(self, response):
        print(response.text)
