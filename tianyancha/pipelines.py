# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
import pymongo

class TianyanchaPipeline(object):
    def __init__(self):
        host = settings['MONGODB_HOST']
        port = settings['MONGODB_PORT']
        dbname = settings['MONGODB_DBNAME']
        client = pymongo.MongoClient(host=host,port=port)
        mdb = client[dbname]
        self.collection = mdb[settings['MONGODB_COLLECTION_RESTORE']]

    def process_item(self, item, spider):
        self.collection.insert(item)
        return item
