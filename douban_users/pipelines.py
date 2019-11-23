# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import asyncio
import motor

import pymongo
from pymysql import cursors
from twisted.enterprise import adbapi
from douban_users.items import DoubanUsersItem, TopicItemsItem, TopicsItem, TopicGalleriesItem


class DoubanTopicPipeline(object):
    '''话题数据存储在MySQL，这是一个总的，但已经分别针对item写了pipeline'''
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        params = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            cursorclass=cursors.DictCursor,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **params)
        return cls(dbpool)

    def process_item(self, item, spider):
        if isinstance(item, TopicGalleriesItem):
            # 利用连接池对象，开始操作数据，将数据写入到数据库中
            query = self.dbpool.runInteraction(self.do_insert, item)
            # 如果异步任务执行失败的话，可以通过ErrBack()进行监听, 给insert添加一个执行失败的回调事件
            query.addErrback(self.handle_error, item, spider)
        return item

    def handle_error(self, failure, item, spider):
        print('-----数据库写入失败', failure)

    def do_insert(self, cursor, item):
        # 从item取得数据
        table, dict_data = item.dict_item()
        # 组建语句和参数
        keys = ', '.join(dict_data.keys())
        value_holders = ', '.join(['%s'] * len(dict_data))
        # if isinstance(item, TopicItemsItem):
        #   # 只为添加一收藏数，无甚用，可弃之
        #     if dict_data['author'] and dict_data['topic']:
        #         updater = ', '.join([f'{key}=%s' for key in dict_data.keys()][1:-1])
        #         params = tuple(dict_data.values()) + tuple(dict_data.values())[1:-1]
        #     else:
        #         updater = 'collect_count=%s'
        #         param_deal = list(dict_data.values()) + [dict_data['collect_count']]
        #         params = tuple(param_deal)
        # else:
        #     updater = ', '.join([f'{key}=%s' for key in dict_data.keys()][1:])
        #     params = tuple(dict_data.values()) + tuple(dict_data.values())[1:]

        updater = ', '.join([f'{key}=%s' for key in dict_data.keys()][1:])
        params = tuple(dict_data.values()) + tuple(dict_data.values())[1:]
        insert_sql = f'INSERT INTO {table}({keys}) VALUES({value_holders}) ON DUPLICATE KEY UPDATE {updater}'
        # 执行插入语句
        cursor.execute(insert_sql, params)


class DoubanTopicItemMongoPipeline(object):
    '''用户发布的广播日记等，存储在mongodb中'''
    @classmethod
    def from_settings(cls, settings):
        cls.mongo_host = settings['MONGODB_HOST']
        cls.db_name = settings['MONGODB_NAME']
        return cls()

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_host)
        self.db = self.client[self.db_name]
        self.collection = self.db['topic_items']

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, TopicItemsItem):
            item = dict(item)
            topic_item = self.collection.find_one({'_id': item['_id']})
            if not topic_item:
                result = self.collection.insert_one(item)
            else:
                result = self.collection.update_one(
                    topic_item, {'$set': {'praise_count': item['praise_count'],
                                          'comment_count': item['comment_count'],
                                          'share_count': item['share_count'],
                                          }
                                 }
                )
        return item


class DoubanUserPipeline(object):
    '''用户user数据，存储在mongodb中'''
    @classmethod
    def from_settings(cls, settings):
        cls.mongo_host = settings['MONGODB_HOST']
        cls.db_name = settings['MONGODB_NAME']
        return cls()

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_host)
        self.db = self.client[self.db_name]
        self.collection = self.db['douban_topic_creators']

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # if isinstance(item, dict):
        # 判断item类型，因为topicitem也是字典，虽然继承了TopicItemsItem，但部分item传递过来竟也是字典，因此多加一个属性判断
        if type(item) == dict and hasattr(item, 'location'):
            user = self.collection.find_one({'_id': item['_id']})
            if not user:
                result = self.collection.insert_one(item)
            else:
                result = self.collection.update_one(
                    user, {'$set': {'location': item['location'],
                                    'books': item['books'],
                                    'movies': item['movies'],
                                    'musics': item['musics'],
                                    'group': item['group'],
                                    'relationship': item['relationship'],
                                    'common_with_me': item['common_with_me'],
                                    }
                           }
                )
        return item

