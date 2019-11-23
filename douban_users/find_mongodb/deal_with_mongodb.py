import json
from collections import Counter

import pymongo

class GetIds():

    def __init__(self):
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = client['my_mongodb']

    def get_topic_infos(self):
        # 获取话题文章数和id，返回一个字典
        collection = self.db['douban_topics']
        topic_id_mongo = collection.find({}, {'_id': 1, 'post_count': 1})
        topic_infos = {x['_id']:x['post_count'] for x in topic_id_mongo}
        return topic_infos

    def get_topic_creator_ids(self):
        collection = self.db['douban_topics']
        topic_id_result = collection.find({}, {'topic_creator': True, '_id': False})
        id_counter = Counter([x['topic_creator'] for x in topic_id_result])
        topic_creator_ids = list(id_counter.keys())
        with open('find_mongodb/topic_creators.txt', 'w') as f:
            f.write(json.dumps(topic_creator_ids))

    def red_ids(self):
        with open('find_mongodb/topic_creators.txt','r') as f:
            ids_str = f.read()
            ids = json.loads(ids_str)
        return ids

    def read_second_ids(self):
        collection = self.db['douban_topic_creators']
        topic_id_result = collection.find({}, {'_id': True})
        id_list = [x['_id'] for x in topic_id_result]
        with open('find_mongodb/first_user_ids.txt', 'w') as f:
            f.write(json.dumps(id_list))
        return id_list

    def deal_with_left_two(self):
        to_insert = [{
            '_id': 1312772,
            'name': '螃蟹|Daddy²',
            'uid': 'faceChrist',
            'reg_time': '2006-11-12',
            'location': {
                'city_id': '',
                'city': 'Melbourne, Australia',
            },
            'books': {
                'doing': 3,
                'wish': 148,
                'collect': 62,
            },
            'movies': {
                'doing': 48,
                'wish': 323,
                'collect': 1074,
            },
            'musics': {
                'doing': 2,
                'wish': 19,
                'collect': 205,
            },
            'group': 45,
            'relationship': {
                'following': 142,
                'follower': 22829,
            },
            'common_with_me': 161,
        },
            {
                '_id': 130535307,
                'name': '小李²不讲道理',
                'uid': '130535307',
                'reg_time': '2015-07-01',
                'location': {
                    'city_id': '',
                    'city': '浙江杭州',
                },
                'books': {
                    'doing': 2,
                    'wish': 2,
                    'collect': 12,
                },
                'movies': {
                    'doing': 4,
                    'wish': 33,
                    'collect': 365,
                },
                'musics': {
                    'doing': 0,
                    'wish': 0,
                    'collect': 1,
                },
                'group': 53,
                'relationship': {
                    'following': 31,
                    'follower': 18,
                },
                'common_with_me': 103,
            }]
        collection = self.db['douban_topic_creators']
        result = collection.insert_many(to_insert, ordered=False)
        print(result.insert_ids)

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

if __name__ == '__main__':
    id_getter = GetIds()
    # topic_ids = id_getter.read_txt('topic_ids.txt')
    topic_infos = id_getter.get_topic_infos()
    id_getter.write_txt(topic_infos, 'topic_infos.txt')
    # id_getter.get_topic_creator_ids()
    # creator_ids = id_getter.red_ids()
    # # id_getter.deal_with_left_two()
    # user_ids = id_getter.read_second_ids()
    # ids_left = []
    # for id in creator_ids[1:]:
    #     if id not in user_ids:
    #         ids_left.append(id)
    # id_getter.write_txt(ids_left, 'find_mongodb/inlegal_ids.txt')
