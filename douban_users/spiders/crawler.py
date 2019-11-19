# -*- coding: utf-8 -*-
import json
import re
import time

import scrapy
from scrapy import http
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from douban_users.items import TopicGalleriesItem, TopicsItem, TopicItemsItem, ItemDownloader, DoubanUsersItem

class CrawlerSpider(CrawlSpider):
    name = 'crawler'
    allowed_domains = ['douban.com', 'www.douban.com', 'm.douban.com']
    start_urls = ['https://www.douban.com/gallery/all', ]

    allow_get_person_urls = (
        'note/\d+',
        'people/\d+/status/\d+',
        '/gallery/topic/\d+',
    )
    allow_person_urls = (
        '/people/\d+',
    )
    rules = (
        Rule(LinkExtractor(allow=allow_get_person_urls), follow=True,),
        Rule(LinkExtractor(allow=allow_person_urls,), callback='parse_person', follow=True,),
    )

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
            topic_item['id'] = int(topic['id'])
            topic_item['subtitle'] = topic.get('subtitle', '')
            topic_item['name'] = topic['name']
            topic_item['gallery'] = int(topic['column']['id'])
            topic_item['abstract'] = topic.get('introduction', '')
            topic_item['read_count'] = topic.get('read_count', 0)
            topic_item['subscription_count'] = topic['subscription_count']
            topic_item['participant_count'] = topic['participant_count']
            topic_item['post_count'] = topic['post_count']
            creator_id = topic.get('creator_id')
            topic_item['topic_creator'] = int(creator_id) if creator_id else 1000000
            yield topic_item
            
            topic_url = topic['url']
            topic_meta = {
                'topicid': topic_item['id'],
                'post_count': topic_item['post_count'],
            }
            yield http.Request(url=topic_url, callback=self.get_json_topic, meta=topic_meta)

    def get_json_topic(self, response):
        topic_id = response.meta['topicid']
        post_count = response.meta['post_count']
        step = 30
        for s in range(0, post_count, step):
            topic_json_url = f'https://m.douban.com/rexxar/api/v2/gallery/topic/{topic_id}/items?sort=all&start={s}&count={step}'
            # topic_json_url = f'https://m.douban.com/rexxar/api/v2/gallery/topic/{topic_id}/items?sort=hot&start={s}&count={step}&&guest_only=1&ck=b_lM'
            yield http.Request(url=topic_json_url, callback=self.parse_topic, meta=response.meta)

    def parse_topic(self, response):
        json_response = json.loads(response.text)
        items = json_response['items']
        if items:
            for item in items:
                if not item.get('is_ad', True):
                    target = item['target'].get('status', item['target'])
                    topicitem_item = TopicItemsItem()
                    topicitem_item['id'] = f'{item["target"]["type"]}-{target["id"]}'
                    topicitem_item['title_or_abstract'] = target.get('title', item['abstract'])
                    topicitem_item['topic'] = int(item['topic']['id'])
                    topicitem_item['author'] = target.get('author',{'id':1000000}).get('id')
                    topicitem_item['create_time'] = target['create_time']
                    topicitem_item['status_up_count'] = target.get('like_count',0)
                    topicitem_item['comment_count'] = target['comments_count']
                    topicitem_item['share_count'] = target['reshares_count']
                    topicitem_item['collect_count'] = 0
                    yield topicitem_item
        else:
            time.sleep(10)
            topic_id = response.meta['topicid']
            yield http.Request(url=response.url, callback=self.parse_topic)

    def parse_item(self, response):
        # 解析文章
        # 获取文章收藏数
        item_loader = ItemDownloader(item=TopicItemsItem(), response=response)
        item_loader.add_css('id', 'div.note-container::id')
        item_loader.add_value('title_or_abstract', '')  # EMPTY
        item_loader.add_value('topic', 0)
        item_loader.add_value('author', 0)
        item_loader.add_value('create_time', '0000-00-00')
        item_loader.add_value('status_up_count', 0)
        item_loader.add_value('comment_count', 0)
        item_loader.add_value('share_count', 0)
        item_loader.add_css('collect_count', 'div.action-collect>a>span.react-num::text')

        topicitem_item = item_loader.load_item()
        return topicitem_item

    def parse_person(self,response):
        # 解析用户主页，获取用户信息
        item_user = {}
        item_user['_id'] = response.css('div#profile .user-opt>a::attr(id)').get().strip()
        item_user['name'] = response.css('div#db-usr-profile .info>h1::text').get().strip()
        item_user['uid'] = response.css('div#profile div.user-info>.pl::text').get().strip()
        item_user['reg_time'] = response.css('div#profile div.user-info>.pl::text').getall()[-1].strip()[:-2]
        item_user['location'] = {}
        item_user['location']['city_id'] = ''
        item_user['location']['city'] = response.css('div#profile div.user-info>a::text').get(default='')
        item_user['books'] = {}
        item_user['books']['doing'] = int(response.css('#book>h2>.pl>a[href$="do"]::text').get(default='0000').strip()[:-3])
        item_user['books']['wish'] = int(response.css('#book>h2>.pl>a[href$="wish"]::text').get(default='0000').strip()[:-3])
        item_user['books']['collect'] = int(response.css('#book>h2>.pl>a[href$="collect"]::text').get(default='0000').strip()[:-3])
        item_user['movies'] = {}
        item_user['movies']['doing'] = int(response.css('#movie>h2>.pl>a[href$="do"]::text').get(default='0000').strip()[:-3])
        item_user['movies']['wish'] = int(response.css('#movie>h2>.pl>a[href$="wish"]::text').get(default='0000').strip()[:-3])
        item_user['movies']['collect'] = int(response.css('#movie>h2>.pl>a[href$="collect"]::text').get(default='0000').strip()[:-3])
        item_user['musics'] = {}
        item_user['musics']['doing'] = int(response.css('#music>h2>.pl>a[href$="do"]::text').get(default='0000').strip()[:-3])
        item_user['musics']['wish'] = int(response.css('#music>h2>.pl>a[href$="wish"]::text').get(default='0000').strip()[:-3])
        item_user['musics']['collect'] = int(response.css('#music>h2>.pl>a[href$="collect"]::text').get(default='0000').strip()[:-3])
        item_user['group'] = int(''.join(filter(str.isdigit, response.css('#group>h2::text').get(default='0'))))
        item_user['relationship'] = {}
        item_user['relationship']['following'] = int(''.join(filter(str.isdigit, response.css('div.aside>.rev-link>a::text').get(default='0'))))
        item_user['relationship']['follower'] = int(response.css('div.aside #friend>h2 a::text').get(default='0').strip()[2:])
        item_user['common_with_me'] = int(''.join(filter(str.isdigit, response.css('div#common>h2::text').get(default='0'))))
        yield item_user

    # def parse_item(self, response):
        # item = {}
        # item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        # item['name'] = response.xpath('//div[@id="name"]').get()
        # item['description'] = response.xpath('//div[@id="description"]').get()
        # 获取文章收藏数
        # return item

    
