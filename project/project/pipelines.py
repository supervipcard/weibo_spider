# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

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
        return item
