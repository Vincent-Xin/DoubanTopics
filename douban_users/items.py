# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose


class ItemDownloader(ItemLoader):
    default_output_processor = TakeFirst()


class TopicGalleriesItem(scrapy.Item):
    # 话题分类，如："影视"
    # gallery/all?column_id=(\d+)
    id = scrapy.Field()
    topic_name = scrapy.Field()
    topic_count = scrapy.Field()

    def dict_item(self):
        item_data = {
            'id': self['id'],
            'topic_name': self['topic_name'],
            'topic_count': self['topic_count'],
        }
        table = 'topicgalleries'
        return table, item_data


class TopicsItem(scrapy.Item):
    # 话题，如"对校园霸凌说不"
    _id = scrapy.Field()
    subtitle = scrapy.Field()
    name = scrapy.Field()
    gallery = scrapy.Field()
    abstract = scrapy.Field()
    read_count = scrapy.Field()
    subscription_count = scrapy.Field()
    participant_count = scrapy.Field()
    post_count = scrapy.Field()
    topic_creator = scrapy.Field()

    def dict_item(self):
        item_data = {
            # 'id': self['id'],
            '_id': self['_id'],
            'subtitle': self['subtitle'],
            'name': self['name'],
            'gallery': self['gallery'],
            'abstract': self['abstract'],
            'read_count': self['read_count'],
            'subscription_count': self['subscription_count'],
            'participant_count': self['participant_count'],
            'post_count': self['post_count'],
            'topic_creator': self['topic_creator'],
        }
        table = 'topics'
        return table, item_data

class TopicItemsItem(scrapy.Item):
    # for mongodb
    _id = scrapy.Field()
    type = scrapy.Field()
    title = scrapy.Field()
    abstract = scrapy.Field()
    text = scrapy.Field()
    topic = scrapy.Field()
    author = scrapy.Field()
    author.id = scrapy.Field()
    author.uid = scrapy.Field()
    author.name = scrapy.Field()
    author.city = scrapy.Field()
    author.city_id = scrapy.Field()
    author.reg_time = scrapy.Field()
    create_time = scrapy.Field()
    praise_count = scrapy.Field()
    comment_count = scrapy.Field()
    share_count = scrapy.Field()

# class TopicItemsItem(scrapy.Item):
#     # 话题下发表的广播和日记等内容 forMySQL
#     id = scrapy.Field()
#     title_or_abstract = scrapy.Field()
#     topic = scrapy.Field()
#     author = scrapy.Field()
#     create_time = scrapy.Field()
#     status_up_count = scrapy.Field()
#     comment_count = scrapy.Field()
#     share_count = scrapy.Field()
#     collect_count = scrapy.Field()
#
#     def dict_item(self):
#         item_data = {
#             'id': self['id'],
#             'title_or_abstract': self['title_or_abstract'],
#             'topic': self['topic'],
#             'author': self['author'],
#             'create_time': self['create_time'],
#             'status_up_count': self['status_up_count'],
#             'comment_count': self['comment_count'],
#             'share_count': self['share_count'],
#             'collect_count': self['collect_count'],
#         }
#         table = 'topicitems'
#         return table, item_data


# class DoubanUsersItem(scrapy.Item):
#     user = {}

# class DoubanUsersItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     user = {}
