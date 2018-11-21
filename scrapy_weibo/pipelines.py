# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy_weibo.items import WeiboItem
from pymongo import MongoClient
from scrapy.conf import settings
import logging
class ScrapyWeiboPipeline(object):
    def __init__(self):
        try:
            host = settings['MONGODB_SERVER']
            port = settings['MONGODB_PORT']
            dbname = settings['MONGODB_DBNAME']  # 数据库名
            client = MongoClient(host=host, port=port)
            tdb = client[dbname]
            self.port = tdb[settings['MONGODB_COLLECTION1']]  # 表名
        except Exception as e:
            print("错误信息为",e)
    def process_item(self, item, spider):
        try:
            weiboinfo = dict(item)
            self.port.insert(weiboinfo)
            return item
        except Exception as e:
            print('存入数据库时出错',e)

