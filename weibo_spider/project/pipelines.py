# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
import json
from datetime import datetime, timedelta
import pymysql
from twisted.enterprise import adbapi
from .items import *


class DataCheckPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, MBlogItem):
            item['source'] = item['source'][0] if item['source'] else None
            item['content'] = ' '.join([i.strip().replace('\u200b', '') for i in item['content'] if i.strip()]).strip()
            item['picture'] = json.dumps(item['picture'], ensure_ascii=False) if item['picture'] else None
            item['video'] = json.dumps(item['video'], ensure_ascii=False) if item['video'] else None
            if '转发' in item['forward_count']:
                item['forward_count'] = 0
            elif '100万+' in item['forward_count']:
                item['forward_count'] = 1000000
            else:
                item['forward_count'] = int(item['forward_count'])
            if '评论' in item['comment_count']:
                item['comment_count'] = 0
            elif '100万+' in item['comment_count']:
                item['comment_count'] = 1000000
            else:
                item['comment_count'] = int(item['comment_count'])
            if '赞' in item['like_count']:
                item['like_count'] = 0
            elif '100万+' in item['like_count']:
                item['like_count'] = 1000000
            else:
                item['like_count'] = int(item['like_count'])
        if isinstance(item, CommentItem):
            item['content'] = ' '.join([i.strip().replace('\u200b', '') for i in item['content'] if i.strip()]).lstrip('：').strip()
            item['picture'] = json.dumps(item['picture'], ensure_ascii=False) if item['picture'] else None
            item['like_count'] = int(item['like_count']) if item['like_count'] != '赞' else 0
            item['time'] = re.sub(r'第\d+楼', '', item['time']).strip()
            if '秒前' in item['time']:
                item['time'] = (datetime.now() - timedelta(seconds=int(item['time'].replace('秒前', '')))).strftime('%Y-%m-%d %H:%M')
            elif '分钟前' in item['time']:
                item['time'] = (datetime.now() - timedelta(minutes=int(item['time'].replace('分钟前', '')))).strftime('%Y-%m-%d %H:%M')
            elif '今天' in item['time']:
                item['time'] = item['time'].replace('今天', datetime.now().strftime('%Y-%m-%d'))
            elif '月' in item['time'] and '日' in item['time'] and '年' not in item['time']:
                item['time'] = str(datetime.now().year) + '-' + item['time'].replace('月', '-').replace('日', '')
            elif re.search(r'\d+-\d+-\d+ \d+:\d+', item['time']):
                pass
            else:
                raise Exception('评论时间无法解析')
        if isinstance(item, UserItem):
            item['headPortrait'] = item['headPortrait'] if item['headPortrait'] != '//ww1.sinaimg.cn/default/images/default_avatar_male_uploading_180.gif' else None
            item['membershipGrade'] = int(re.search(r'icon_member(\d)', item['membershipGrade'][0]).group(1)) if item['membershipGrade'] and re.search(r'icon_member(\d)', item['membershipGrade'][0]) else None
            item['identity'] = item['identity'][0].strip() if item['identity'] else None
            item['identity'] = item['identity'] if item['identity'] else None
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
            item['domainHacks'] = json.dumps(item['domainHacks'], ensure_ascii=False) if item.get('domainHacks') else None
            item['email'] = item['email'][0].strip() if item.get('email') else None
            item['qq'] = item['qq'][0].strip() if item.get('qq') else None
            item['msn'] = item['msn'][0].strip() if item.get('msn') else None
            item['jobInformation'] = json.dumps(item['jobInformation'], ensure_ascii=False) if item.get('jobInformation') else None
            item['educationInformation'] = json.dumps(item['educationInformation'], ensure_ascii=False) if item.get('educationInformation') else None
            item['tabs'] = json.dumps(item['tabs'], ensure_ascii=False) if item.get('tabs') else None
            item['following'] = int(item['following'])
            item['followers'] = int(item['followers'])
            item['mblogNum'] = int(item['mblogNum'])
            if item['approveType']:
                if 'icon_pf_approve_co' in item['approveType'][0]:
                    item['approveType'] = '官方认证'
                elif 'icon_pf_approve_gold' in item['approveType'][0]:
                    item['approveType'] = '金V认证'
                elif 'icon_pf_approve' in item['approveType'][0]:
                    item['approveType'] = '个人认证'
                else:
                    item['approveType'] = None
            else:
                item['approveType'] = None
        return item


class SqlPipeline(object):
    def __init__(self, pool):
        self.db_conn = pool
        self.mblog_sql = 'insert ignore into mblog values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        self.comment_sql = 'insert ignore into comment values (%s, %s, %s, %s, %s, %s, %s, %s)'
        self.user_sql = 'insert ignore into user values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

    @classmethod
    def from_settings(cls, settings):
        pool = adbapi.ConnectionPool('pymysql', host=settings['MYSQL_HOST'], port=settings['MYSQL_PORT'], user=settings['MYSQL_USER'], passwd=settings['MYSQL_PASSWORD'], db=settings['MYSQL_DB'], charset=settings['MYSQL_CHARSET'])
        return cls(pool)

    def process_item(self, item, spider):
        query = self.db_conn.runInteraction(self.go_insert, item)   # 数据插入
        query.addErrback(self.handle_error, item, spider)   # 异常检测
        return item

    def go_insert(self, cursor, item):
        if isinstance(item, MBlogItem):
            cursor.execute(self.mblog_sql, [item['mid'], item['uid'], item['url'], item['time'], item['source'],
                                            item['content'], item['picture'], item['video'], item['forward_count'],
                                            item['comment_count'], item['like_count'], datetime.now()])
        if isinstance(item, CommentItem):
            cursor.execute(self.comment_sql, [item['comment_id'], item['mid'], item['uid'], item['content'],
                                              item['picture'], item['time'], item['like_count'], datetime.now()])
        if isinstance(item, UserItem):
            cursor.execute(self.user_sql, [item['uid'], item['nickname'], item['headPortrait'], item['membershipGrade'],
                                           item['approveType'], item['identity'], item['realName'], item['area'], item['sex'],
                                           item['sexualOrientation'], item['relationshipStatus'], item['birthday'],
                                           item['bloodType'], item['blog'], item['intro'],item['registrationDate'],
                                           item['domainHacks'], item['email'], item['qq'],item['msn'],
                                           item['jobInformation'], item['educationInformation'], item['tabs'],
                                           item['following'], item['followers'], item['mblogNum'], item['url'], datetime.now()])

    def handle_error(self, failure, item, spider):
        spider.logger.error(failure)
