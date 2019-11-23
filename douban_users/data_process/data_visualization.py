# import pyecharts
# from pyecharts.charts import Bar
# from pyecharts import options as opt
# from pyecharts.render import make_snapshot
# from snapshot_selenium import snapshot
import matplotlib
from matplotlib import pyplot as plt

from data_process.get_datas import GetDataFromDB

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus']=False

data_getter = GetDataFromDB()
# 14494
# topic_total = data_getter.get_topic_total()
gallery_counts = data_getter.get_gallery_counts()
data = list(gallery_counts.values())
x_labels = list(gallery_counts.keys())
plt.bar(x_labels, data, width=0.5, color='b', alpha=0.7)
plt.tick_params(axis='x', labelsize=8, labelrotation=-45)
plt.xlabel("话题分类", fontsize=12)
plt.ylabel("话题数", fontsize=12)
for key,value in gallery_counts.items():
    plt.text(key, value, value, ha='center', fontsize=8, va='bottom', rotation=45)
plt.title("豆瓣话题分类数")
plt.savefig('豆瓣话题分类数.svg', bbox_inches='tight')