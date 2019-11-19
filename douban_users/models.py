from peewee import *

db = MySQLDatabase('python_spider', user='root', password='xinyuanchang', host="localhost", port=3306, charset='utf8')


class BaseModel(Model):
    class Meta:
        database = db

class TopicGalleries(BaseModel):
    # 话题分类，如："影视"
    # gallery/all?column_id=(\d+)
    id = IntegerField(primary_key=True)
    topic_name = CharField(verbose_name="分类名称")
    topic_count = IntegerField(default=0, verbose_name="话题数量")


class Topics(BaseModel):
    # 话题，如"对校园霸凌说不"
    id = IntegerField(primary_key=True)
    subtitle = CharField(default='', verbose_name="次级话题？")
    name = CharField(max_length=255, verbose_name="话题题目")
    gallery = IntegerField(verbose_name="所属话题分类id")
    abstract = TextField(default='', verbose_name="话题描述")
    read_count = IntegerField(default=0, verbose_name="浏览量")
    subscription_count = IntegerField(verbose_name="关注人数")
    participant_count = IntegerField(verbose_name="参与人数/次数？")
    post_count = IntegerField(default=0, verbose_name="内容数")
    topic_creator = IntegerField(verbose_name="话题发起人id")


class TopicItems(BaseModel):
    # 发表的广播和日记等话题下内容
    id = CharField(primary_key=True)
    title_or_abstract = CharField(verbose_name="日记题目或者广播摘要")
    topic = IntegerField(default=0, verbose_name="所属话题id")
    author = IntegerField(default=0, verbose_name="作者")
    create_time = DateTimeField(default='', verbose_name="发布时间")
    status_up_count = IntegerField(default=0, verbose_name="点赞数")
    comment_count = IntegerField(default=0, verbose_name="评论数")
    share_count = IntegerField(default=0, verbose_name="转播数")
    collect_count = IntegerField(default=0, verbose_name="收藏数")
    # donate_num = IntegerField(default=0, verbose_name="赞赏数")

if __name__ == '__main__':
    db.connect()
    if not db.table_exists(['topicgalleries', 'topics', 'topicitems']):
        db.create_tables([TopicGalleries, Topics, TopicItems])


