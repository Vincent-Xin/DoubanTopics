# -*- coding: utf-8 -*-
import json
import re
import time

import scrapy
from scrapy import http
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from douban_users.items import TopicGalleriesItem, TopicsItem, TopicItemsItem, ItemDownloader


class CrawlerSpider(CrawlSpider):
    name = 'crawler'
    allowed_domains = ['douban.com', 'www.douban.com', 'm.douban.com']
    start_urls = ['https://www.douban.com/gallery/all', ]

    step = 30

    allow_get_person_urls = (
        'note/732089483/?type=rec#sep', 'note/732089483/?type=like#sep',
        'note/732089483/?type=collect#sep', 'note/732089483/?type=donate#sep',
        'people/152467430/status/2534401953/?tab=reshare#sep', 'people/152467430/status/2534401953/?tab=like#sep',
        'people/152467430/status/2534401953/?tab=collect#sep',
    )
    allow_person_urls = (
        '/people/39523317/', '/people/50177428',
    )
    allow_item_urls = (
        'note/\d+/', 'note/\d+', 'people/\d+/status/\d+', 'people/\d+/status/\d+/',
        'doubanapp/dispatch?uri=/status/2534401953/', 'doubanapp/dispatch?uri=/note/732089483/',
    )
    rules = (
        Rule(LinkExtractor(allow=allow_get_person_urls), follow=True),
        Rule(LinkExtractor(allow=allow_person_urls), callback='parse_person', follow=True, process_request='add_cookie'),
        Rule(LinkExtractor(allow=allow_item_urls), callback='parse_item',follow=True),
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
            step = self.step
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
        step = self.step
        for s in range(0, post_count, step):
            headers = {
                # 'Cookie': 'bid=NulHfSznh4Q; douban-fav-remind=1; _vwo_uuid_v2=DC7E299AC0DCAD57725551FB3E9BC52E6|79770cc69479b99098ad9e06c26a2748; push_doumail_num=0; gr_user_id=8ba9f9a6-9872-4f54-9e64-59e2e2ca590f; douban-profile-remind=1; viewed="30175598"; ct=y; dbcl2="51476394:C+2jKwPVY1c"; ck=b_lM; push_noty_num=0; loc-last-index-location-id="108296"; ll="108296"; ap_v=0,6.0',
                # 'Cookie': 'bid=NulHfSznh4Q; douban-fav-remind=1; _vwo_uuid_v2=DC7E299AC0DCAD57725551FB3E9BC52E6|79770cc69479b99098ad9e06c26a2748; push_doumail_num=0; gr_user_id=8ba9f9a6-9872-4f54-9e64-59e2e2ca590f; douban-profile-remind=1; viewed="30175598"; ct=y; dbcl2="51476394:C+2jKwPVY1c"; push_noty_num=0; loc-last-index-location-id="108296"; ll="108296"; ap_v=0,6.0; ck=b_lM; frodotk="6d334efef6796bec4799ecfce36c43c4"',
                'Referer': f'https://www.douban.com/gallery/topic/{topic_id}/',
            }
            topic_json_url = f'https://m.douban.com/rexxar/api/v2/gallery/topic/{topic_id}/items?sort=new&start={s}&count={step}'
            # topic_json_url = f'https://m.douban.com/rexxar/api/v2/gallery/topic/{topic_id}/items?sort=hot&start={s}&count={step}&&guest_only=1&ck=b_lM'
            yield http.Request(url=topic_json_url, callback=self.parse_topic, meta=response.meta, headers=headers)

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
                    topicitem_item['author'] = target['author']['id']
                    topicitem_item['create_time'] = target['create_time']
                    topicitem_item['status_up_count'] = target['like_count']
                    topicitem_item['comment_count'] = target['comments_count']
                    topicitem_item['share_count'] = target['reshares_count']
                    topicitem_item['collect_count'] = 0
                    yield topicitem_item
        else:
            time.sleep(10)
            topic_id = response.meta['topicid']
            headers = {
                # 'Cookie': 'bid=NulHfSznh4Q; douban-fav-remind=1; _vwo_uuid_v2=DC7E299AC0DCAD57725551FB3E9BC52E6|79770cc69479b99098ad9e06c26a2748; push_doumail_num=0; gr_user_id=8ba9f9a6-9872-4f54-9e64-59e2e2ca590f; douban-profile-remind=1; viewed="30175598"; ct=y; dbcl2="51476394:C+2jKwPVY1c"; push_noty_num=0; loc-last-index-location-id="108296"; ll="108296"; ck=b_lM; ap_v=0,6.0; frodotk="88255c7fc844904b9870157f58cdb0e1"',
                # 'Cookie': 'bid=NulHfSznh4Q; douban-fav-remind=1; _vwo_uuid_v2=DC7E299AC0DCAD57725551FB3E9BC52E6|79770cc69479b99098ad9e06c26a2748; push_doumail_num=0; gr_user_id=8ba9f9a6-9872-4f54-9e64-59e2e2ca590f; douban-profile-remind=1; viewed="30175598"; ct=y; dbcl2="51476394:C+2jKwPVY1c"; ck=b_lM; push_noty_num=0; loc-last-index-location-id="108296"; ll="108296"; ap_v=0,6.0',
                # 'Cookie': 'bid=NulHfSznh4Q; douban-fav-remind=1; _vwo_uuid_v2=DC7E299AC0DCAD57725551FB3E9BC52E6|79770cc69479b99098ad9e06c26a2748; push_doumail_num=0; gr_user_id=8ba9f9a6-9872-4f54-9e64-59e2e2ca590f; douban-profile-remind=1; viewed="30175598"; ct=y; dbcl2="51476394:C+2jKwPVY1c"; push_noty_num=0; loc-last-index-location-id="108296"; ll="108296"; ap_v=0,6.0; ck=b_lM; frodotk="6d334efef6796bec4799ecfce36c43c4"',
                'Referer': f'https://www.douban.com/gallery/topic/{topic_id}/',
            }
            yield http.Request(url=response.url, callback=self.parse_topic, headers=headers)

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
        return item_user

    def add_cookies(self, request, response):
        my_cookies = 'bid=NulHfSznh4Q; douban-fav-remind=1; _vwo_uuid_v2=DC7E299AC0DCAD57725551FB3E9BC52E6|79770cc69479b99098ad9e06c26a2748; push_doumail_num=0; gr_user_id=8ba9f9a6-9872-4f54-9e64-59e2e2ca590f; douban-profile-remind=1; viewed="30175598"; ct=y; dbcl2="51476394:C+2jKwPVY1c"; ck=b_lM; push_noty_num=0; loc-last-index-location-id="108296"; ll="108296"; ap_v=0,6.0'
        request.headers['Cookie'] = my_cookies

    def process_request(self, request, response):
        pass


    # def parse_item(self, response):
        # item = {}
        # item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        # item['name'] = response.xpath('//div[@id="name"]').get()
        # item['description'] = response.xpath('//div[@id="description"]').get()
        # 获取文章收藏数
        # return item

    # item_author = {}
    # item_author['_id'] = target['author']['id'].strip()
    # item_author['name'] = target['author']['name']
    # item_author['uid'] = target['author']['uid']
    # item_author['reg_time'] = target['author']['reg_time']
    # item_author['location'] = {}
    # item_author['location']['city_id'] = target['author']['loc']['id']
    # item_author['location']['city'] = target['author']['loc']['name']
    # # item_author['article_nums'] = 1
    # # item_author['topic_nums'] = 0
    # yield item_author

    # topic_author = {}
    # topic_author['_id'] = items[0]['topic']['creator']['id'].strip()
    # topic_author['name'] = items[0]['topic']['creator']['name']
    # topic_author['uid'] = items[0]['topic']['creator']['uid']
    # topic_author['reg_time'] = items[0]['topic']['creator']['reg_time']
    # topic_author['location'] = {}
    # topic_author['location']['city_id'] = items[0]['topic']['creator']['loc']['id']
    # topic_author['location']['city'] = items[0]['topic']['creator']['loc']['name']
    # # topic_author['topic_nums'] = 1
    # # topic_author['article_nums'] = 0
    # yield topic_author