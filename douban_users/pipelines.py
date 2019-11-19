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
from douban_users.items import DoubanUsersItem, TopicItemsItem

class DoubanTopicPipeline(object):

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
        if not isinstance(item, dict):
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
        if isinstance(item, TopicItemsItem):
            if dict_data['author'] and dict_data['topic']:
                updater = ', '.join([f'{key}=%s' for key in dict_data.keys()][1:-1])
                params = tuple(dict_data.values()) + tuple(dict_data.values())[1:-1]
            else:
                updater = 'collect_count=%s'
                param_deal = list(dict_data.values()) + [dict_data['collect_count']]
                params = tuple(param_deal)
        else:
            updater = ', '.join([f'{key}=%s' for key in dict_data.keys()][1:])
            params = tuple(dict_data.values()) + tuple(dict_data.values())[1:]
        insert_sql = f'INSERT INTO {table}({keys}) VALUES({value_holders}) ON DUPLICATE KEY UPDATE {updater}'
        # 执行插入语句
        cursor.execute(insert_sql, params)

    # def process_item(self, item, spider):
    #     return item

class DoubanUserPipeline(object):

    @classmethod
    def from_settings(cls, settings):
        cls.mongo_host = settings['MONGODB_HOST']
        cls.db_name = settings['MONGODB_NAME']
        return cls()

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_host)
        self.db = self.client[self.db_name]
        self.collection = self.db['douban_users']

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, dict):
            user = self.collection.find_one({'id': item['id']})
            if not user:
                result = self.collection.insert_one(item)
        return item
