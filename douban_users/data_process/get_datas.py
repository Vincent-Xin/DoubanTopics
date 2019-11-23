import json
from collections import Counter

import pymongo
from matplotlib import pyplot as plt


class GetDataFromDB():

    def __init__(self):
        client = pymongo.MongoClient(host='localhost', port=27017)
        db = client.my_mongodb
        self.cltn_galleries = db.topic_galleries
        self.cltn_creators = db.douban_topic_creators
        self.cltn_topics = db.douban_topics

    def get_gallery_counts(self):
        # 获取每类话题的数量，返回一个字典
        gallery_counts = self.cltn_galleries.find({}, {'_id': 0, 'topic_count': 1, 'gallery_name': 1}).sort('topic_count', pymongo.DESCENDING)
        gallery_dict = {x['gallery_name']:x['topic_count'] for x in gallery_counts}
        return gallery_dict

    def get_topic_total(self):
        # 计算话题总数
        topic_counts = self.cltn_galleries.find({}, {'_id': 0, 'topic_count': 1})
        topic_total = sum(x['topic_count'] for x in topic_counts)
        return topic_total

    def get_topic_counts(self, key_name):
        # 查询返回某字段的值和id，并按降序排序
        topic_counts = self.cltn_topics.find({}, {key_name: 1}).sort(key_name, pymongo.DESCENDING)
        return topic_counts

    def get_sometopic_data(self, id, key_name):
        # 查询某id的某值
        topic_data = self.cltn_topics.find({'_id': id}, {'_id': 1, key_name: 1})
        return topic_data

    def get_creator_counts(self):
        # 获取话题创建者的数量和每个创建者创建话题数
        # 返回一个Counter对象
        creators = self.cltn_creators.find({}, {'_id': False, 'topic_creator': True})
        creator_counts = Counter([x['topic_creator'] for x in creators])
        return creator_counts

    def get_creator_cities(self):
        # 获取话题创建者的城市，并计算每个城市的创建者数量
        # 返回一个Counter对象
        creator_cities = self.cltn_creators.find({}, {'_id': 0, 'location.city': 1})
        city_counter = Counter(creator_cities)
        return city_counter

    def write_txt(self, data, filename):
        with open(filename, 'w') as f:
            if isinstance(data, str):
                f.write(data)
            else:
                f.write(json.dumps(data))

    def read_txt(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.loads(f.read())
        except FileNotFoundError:
            print(f'{filename} is not there!')
        else:
            return data
