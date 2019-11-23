# -*- coding: utf-8 -*-
import json
import re

import pymongo
import scrapy


class TopicCreateorsSpider(scrapy.Spider):
    name = 'topic_creators'
    allowed_domains = ['douban.com']
    deny_domains = ['']
    start_urls = ['http://www.douban.com/']

    def start_requests(self):
        # 获取保存在本地的topic_creator_ids
        with open('douban_users/find_mongodb/topic_creators.txt', 'r') as f:
            ids_str = f.read()
            topic_creator_ids = json.loads(ids_str)

        # 第一个为1000000，有些话题没有创建者，设置为1000000，阿北为1000001
        for id in topic_creator_ids[1:]:
            user_url = f'https://www.douban.com/people/{id}/'
            yield scrapy.http.Request(url=user_url, callback=self.parse_person,meta={'id':id})

    def parse_person(self, response):
        if response.status >= 300:
            yield scrapy.http.Request(url=response.url, callback=self.parse_person, meta=response.meta)
        # 解析用户主页，获取用户信息
        else:
            item_user = {}
            item_user['_id'] = response.meta['id']
            name = response.css('div#db-usr-profile .info>h1::text').get()
            if name:
                item_user['name'] = name.strip()
                item_user['uid'] = response.css('div#profile div.user-info>.pl::text').get().strip()
                item_user['reg_time'] = response.css('div#profile div.user-info>.pl::text').getall()[-1].strip()[:-2]

                item_user['location']={}
                item_user['location']['city_id'] = ''
                item_user['location']['city'] = response.css('div#profile div.user-info>a::text').get(default='人间')

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

                group = ''.join(filter(str.isdigit, response.css('#group>h2::text').get(default='0'))).replace(name.strip(), '')
                item_user['group'] = int(group) if group and group != ' ' else 0

                item_user['relationship'] = {}
                item_user['relationship']['follower'] = int(''.join(filter(str.isdigit, response.css('div.aside>.rev-link>a::text').get(default='0'))).replace(name.strip(), ''))
                item_user['relationship']['following'] = int(response.css('div.aside #friend>h2 a::text').get(default='000').strip()[2:])

                common_with_me = ''.join(filter(str.isdigit, response.css('div#common>h2::text').get(default='0'))).replace(name.strip(), '')
                item_user['common_with_me'] = int(common_with_me) if common_with_me else 0

                yield item_user

    # def make_topic_creator_url(self):
    #     client = pymongo.MongoClient(self.mongo_host)
    #     db = client[self.db_name]
    #     collection = db['douban_topics']
    #     # topic_id_result = self.collection.aggregate([{'$group': {'_id': '$topic_creator', 'count': {'$sum': 1}}}])
    #     top_id_result = collection.find({}, {'topic_creator': True, '_id': False})
    #     id_counter = Counter([x['topic_creator'] for x in top_id_result])
    #     topic_creator_ids = list(id_counter.keys())
    #     # 第一个为1000000，有些话题没有创建者，设置为1000000，阿北为1000001
    #     for id in topic_creator_ids[1:]:
    #         user_url = f'https://www.douban.com/people/{id}/'
    #         yield scrapy.http.Request(url=user_url, callback=self.parse_person)

    # doumail_href = response.css('#profile a.a-btn.mr5::attr(href)').get()
    # user_id = re.search('doumail/write\?to=(\d+)$', doumail_href).group(1)