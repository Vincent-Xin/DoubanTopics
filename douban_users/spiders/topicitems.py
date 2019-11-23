# -*- coding: utf-8 -*-
import json
import time

import scrapy
from scrapy import http

from douban_users.items import ItemDownloader, TopicItemsItem


class TopicitemsSpider(scrapy.Spider):
    name = 'topicitems'
    allowed_domains = ['douban.com', 'm.douban.com']
    start_urls = ['http://douban.com/']

    def start_requests(self):
        with open('douban_users/find_mongodb/topic_infos.txt', 'r') as f:
            topic_infos = json.loads(f.read())
        for topic_id, post_count in topic_infos.items():
            step = 50
            for s in range(0, post_count, step):
                # topic_json_url = f'https://m.douban.com/rexxar/api/v2/gallery/topic/{topic_id}/items?sort=all&start={s}&count={step}'
                topic_json_url = f'https://m.douban.com/rexxar/api/v2/gallery/topic/{topic_id}/items?sort=all&start={s}&count={step}&status_full_text=1&guest_only=0&ck=sD9U'
                yield http.Request(url=topic_json_url, callback=self.parse_topic, meta={'topic_id': topic_id})

    def parse_topic(self, response):
        # 解析文章json，获取文章数据
        json_response = json.loads(response.text)
        # print(json_response)
        items = json_response['items']
        if items:
            for item in items:
                if not item.get('is_ad', False):
                    target = item['target'].get('status', item['target'])
                    topicitem_item = TopicItemsItem()
                    topicitem_item['_id'] = target["id"]
                    topicitem_item['type'] = item["target"]["type"]
                    topicitem_item['title'] = target.get('title', '')
                    topicitem_item['abstract'] = target.get('abtract', item.get('abstract', ''))
                    topicitem_item['text'] = target.get('text', '')
                    topicitem_item['topic'] = item['topic']['id']
                    topicitem_item['author'] = {}
                    author = target.get('author', target.get('user'))
                    topicitem_item['author']['id'] = author['id']
                    topicitem_item['author']['uid'] = author['uid']
                    topicitem_item['author']['name'] = author['name']
                    author_loc = author['loc']
                    topicitem_item['author']['city']= author_loc['name'] if author_loc else ''
                    topicitem_item['author']['city_id']= author_loc['id'] if author_loc else ''
                    topicitem_item['author']['reg_time'] = author['reg_time']
                    topicitem_item['create_time'] = target['create_time']
                    topicitem_item['praise_count'] = target.get('like_count', target.get('useful_count'))
                    topicitem_item['comment_count'] = target['comments_count']
                    topicitem_item['share_count'] = target['reshares_count']
                    yield topicitem_item

        elif 'invalid_request' in json_response.get('msg', 'no_item'):
            time.sleep(5)
            yield http.Request(url=response.url, callback=self.parse_topic, meta={'topic_id': response.meta['topic_id']})

    # def parse_item(self, response):
    #     # 解析文章
    #     # 获取文章收藏数
    #     item_loader = ItemDownloader(item=TopicItemsItem(), response=response)
    #     item_loader.add_css('id', 'div.note-container::id')
    #     item_loader.add_value('title_or_abstract', '')  # EMPTY
    #     item_loader.add_value('topic', 0)
    #     item_loader.add_value('author', 0)
    #     item_loader.add_value('create_time', '0000-00-00')
    #     item_loader.add_value('status_up_count', 0)
    #     item_loader.add_value('comment_count', 0)
    #     item_loader.add_value('share_count', 0)
    #     item_loader.add_css('collect_count', 'div.action-collect>a>span.react-num::text')
    #
    #     topicitem_item = item_loader.load_item()
    #     return topicitem_item