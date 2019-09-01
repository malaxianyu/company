# -*- coding: utf-8 -*-
import scrapy
import pymongo
import re
from urllib import parse
from tianyancha.settings import *


class TycSpider(scrapy.Spider):
    name = 'tyc'
    allowed_domains = ['tianyancha.com']
    start_urls = ['https://www.tianyancha.com/']
    host = MONGODB_HOST
    port = MONGODB_PORT
    dbname = MONGODB_DBNAME
    client = pymongo.MongoClient(host=host,port=port)
    mdb = client[dbname]
    collection = mdb[MONGODB_COLLECTION_SPIDER]
    results = collection.find()

    def parse(self, response):
        if not self.login_exception(response):
            for info in self.results[10000:20000]:
                reg_name = info['reg_name']
                url = 'https://www.tianyancha.com/search?'
                kw = {'key':reg_name}
                url += parse.urlencode(kw)
                yield scrapy.Request(
                    url, 
                    callback=self.parse_page, 
                    dont_filter = True
                )
        else:
            yield scrapy.Request(
                response.request.meta['redirect_urls'][0],
                dont_filter = True,
                callback=self.parse
            )

    def parse_page(self, response):
        if not self.login_exception(response):
            result_list = response.xpath('//div[@class="result-list sv-search-container"]/div')
            if result_list:
                for temp in result_list:
                    detail_url = temp.xpath('.//div[@class="header"]/a/@href').extract_first()
                    yield scrapy.Request(
                        detail_url,
                        callback=self.parse_detail,
                        dont_filter = True
                    )
        else:
            yield scrapy.Request(
                response.request.meta['redirect_urls'][0],
                dont_filter = True,
                callback=self.parse_page
            )


    def parse_detail(self, response):
        if not self.login_exception(response):
            item = {}
            item['name'] = response.xpath('//div[@class="content"]/div[@class="header"]/*[@class="name"]/text()').extract_first()
            tr_list = response.xpath('//table[@class="table -striped-col -border-top-none -breakall"]//tr')
            for tr in tr_list:
                text = tr.xpath('.//text()').extract()
                if len(text) % 2 ==1:
                    text = text[:-1]
                for i in range(0, len(text), 2):
                    item[text[i]] = text[i+1]
            yield item
        else:
            yield scrapy.Request(
                response.request.meta['redirect_urls'][0],
                dont_filter = True,
                callback=self.parse_detail
            )

    def login_exception(self, response):
        if re.match('.*login\?from=.*',response.url):
            return True
