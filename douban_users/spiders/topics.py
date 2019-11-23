# -*- coding: utf-8 -*-
import json
import re
import time

import scrapy
from scrapy import http
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from douban_users.items import TopicGalleriesItem, TopicsItem, TopicItemsItem, ItemDownloader, DoubanUsersItem


class TopicsSpider(scrapy.Spider):
    name = 'topics'
    allowed_domains = ['douban.com', 'www.douban.com', 'm.douban.com']
    start_urls = ['https://www.douban.com/gallery/all', ]

    def parse(self, response):
        pass

    def parse_start_url(self, response):
        topics = response.xpath('//div[@class="article"]/section[@class="topic-tabs"]/a[@class="topic-tab-btn "]')
        for topic in topics:
            galleries_item = TopicGalleriesItem()
            gallery_id = int(re.search('gallery/all\?column_id=(\d+)', topic.xpath('./@href').get()).group(1))
            galleries_item['id'] = gallery_id
            galleries_text = topic.xpath('./span/text()').getall()
            galleries_item['topic_name'] = galleries_text[0]
            topic_count = int(re.search('\((\d+)\)', galleries_text[1]).group(1))
            galleries_item['topic_count'] = topic_count
            yield galleries_item
            step = 30
            for s in range(0, topic_count, step):
                gallery_json_url = f'https://www.douban.com/j/gallery/topics?count={step}&start={s}&all=1&column_id={gallery_id}'
                yield http.Request(url=gallery_json_url, callback=self.parse_gallery)

    def parse_gallery(self, response):
        json_response = json.loads(response.text)
        for topic in json_response['topics']:
            topic_item = TopicsItem()
            topic_item['_id'] = int(topic['id'])
            topic_item['subtitle'] = topic.get('subtitle', '')
            topic_item['name'] = topic['name']
            topic_item['gallery'] = int(topic['column']['id'])
            topic_item['abstract'] = topic.get('introduction', '')
            topic_item['read_count'] = topic.get('read_count', 0)
            topic_item['subscription_count'] = topic['subscription_count']
            topic_item['participant_count'] = topic['participant_count']
            topic_item['post_count'] = topic['post_count']
            # 有可能是''
            creator_id = topic.get('creator_id')
            topic_item['topic_creator'] = int(creator_id) if creator_id else 1000000
            yield topic_item

            # topic_url = topic['url']
            # topic_meta = {
            #     'topicid': topic_item['id'],
            #     'post_count': topic_item['post_count'],
            # }
            # yield http.Request(url=topic_url, callback=self.get_json_topic, meta=topic_meta)

    # def get_json_topic(self, response):
    #     topic_id = response.meta['topicid']
    #     post_count = response.meta['post_count']
    #     step = 30
    #     for s in range(0, post_count, step):
    #         topic_json_url = f'https://m.douban.com/rexxar/api/v2/gallery/topic/{topic_id}/items?sort=all&start={s}&count={step}'
    #         # topic_json_url = f'https://m.douban.com/rexxar/api/v2/gallery/topic/{topic_id}/items?sort=hot&start={s}&count={step}&&guest_only=1&ck=b_lM'
    #         yield http.Request(url=topic_json_url, callback=self.parse_topic, meta=response.meta)

    # def parse_topic(self, response):
    #     # 解析文章，获取文章数据
    #     json_response = json.loads(response.text)
    #     items = json_response['items']
    #     if items:
    #         for item in items:
    #             if not item.get('is_ad', True):
    #                 target = item['target'].get('status', item['target'])
    #                 topicitem_item = TopicItemsItem()
    #                 topicitem_item['id'] = f'{item["target"]["type"]}-{target["id"]}'
    #                 topicitem_item['title_or_abstract'] = target.get('title', item['abstract'])
    #                 topicitem_item['topic'] = int(item['topic']['id'])
    #                 topicitem_item['author'] = target.get('author',{'id':1000000}).get('id')
    #                 topicitem_item['create_time'] = target['create_time']
    #                 topicitem_item['status_up_count'] = target.get('like_count',0)
    #                 topicitem_item['comment_count'] = target['comments_count']
    #                 topicitem_item['share_count'] = target['reshares_count']
    #                 topicitem_item['collect_count'] = 0
    #                 yield topicitem_item
    #     else:
    #         time.sleep(10)
    #         topic_id = response.meta['topicid']
    #         yield http.Request(url=response.url, callback=self.parse_topic)

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