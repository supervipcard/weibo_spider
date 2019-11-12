# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
from datetime import datetime, timedelta
from .items import *


class DataCheckPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, MBlogItem):
            item['source'] = item['source'][0] if item['source'] else None
            item['content'] = ''.join([i.strip().replace('\u200b', '') for i in item['content'] if i.strip()]).strip()
            item['picture'] = item['picture'] if item['picture'] else None
            item['video'] = item['video'] if item['video'] else None
            item['forward_count'] = int(item['forward_count']) if item['forward_count'] != '转发' else 0
            item['comment_count'] = int(item['comment_count']) if item['comment_count'] != '评论' else 0
            item['like_count'] = int(item['like_count']) if item['like_count'] != '赞' else 0
        if isinstance(item, CommentItem):
            item['content'] = ''.join([i.strip() for i in item['content'] if i.strip()]).lstrip('：').strip()
            item['picture'] = item['picture'] if item['picture'] else None
            item['like_count'] = int(item['like_count']) if item['like_count'] != '赞' else 0
            if '秒前' in item['time']:
                item['time'] = (datetime.now() - timedelta(seconds=int(item['time'].replace('秒前', '')))).strftime('%Y-%m-%d %H:%M')
            elif '分钟前' in item['time']:
                item['time'] = (datetime.now() - timedelta(minutes=int(item['time'].replace('分钟前', '')))).strftime('%Y-%m-%d %H:%M')
            elif '今天' in item['time']:
                item['time'] = item['time'].replace('今天', datetime.now().strftime('%Y-%m-%d'))
            elif '月' in item['time'] and '日' in item['time']:
                item['time'] = str(datetime.now().year) + '-' + item['time'].replace('月', '-').replace('日', '')
            else:
                raise Exception('评论时间无法解析')
        if isinstance(item, UserItem):
            item['headPortrait'] = item['headPortrait'] if item['headPortrait'] != '//ww1.sinaimg.cn/default/images/default_avatar_male_uploading_180.gif' else None
            item['membershipGrade'] = int(re.search(r'icon_member(\d)', item['membershipGrade'][0]).group(1)) if item['membershipGrade'] and re.search(r'icon_member(\d)', item['membershipGrade'][0]) else None
            item['identity'] = item['identity'][0].strip() if item['identity'] else None
            item['realName'] = item['realName'][0].strip() if item.get('realName') else None
            item['area'] = item['area'][0].strip() if item.get('area') else None
            item['sex'] = item['sex'][0].strip() if item.get('sex') else None
            item['sexualOrientation'] = item['sexualOrientation'][0].strip() if item.get('sexualOrientation') else None
            item['relationshipStatus'] = item['relationshipStatus'][0].strip() if item.get('relationshipStatus') else None
            item['birthday'] = item['birthday'][0].strip() if item.get('birthday') else None
            item['bloodType'] = item['bloodType'][0].strip() if item.get('bloodType') else None
            item['blog'] = item['blog'][0].strip() if item.get('blog') else None
            item['intro'] = item['intro'][0].strip() if item.get('intro') else None
            item['registrationDate'] = item['registrationDate'][0].strip() if item.get('registrationDate') else None
            item['domainHacks'] = item['domainHacks'] if item.get('domainHacks') else None
            item['email'] = item['email'][0].strip() if item.get('email') else None
            item['qq'] = item['qq'][0].strip() if item.get('qq') else None
            item['msn'] = item['msn'][0].strip() if item.get('msn') else None
            item['jobInformation'] = item['jobInformation'] if item.get('jobInformation') else None
            item['educationInformation'] = item['educationInformation'] if item.get('educationInformation') else None
            item['tabs'] = item['tabs'] if item.get('tabs') else None
            item['following'] = int(item['following'])
            item['followers'] = int(item['followers'])
            item['mblogNum'] = int(item['mblogNum'])
            if item['identity'] == item['intro']:
                item['identity'] = None
        return item
