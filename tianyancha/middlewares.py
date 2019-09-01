# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import scrapy
from scrapy import signals
import base64
import logging
import re

from .utils import fetch_one_proxy

# 非开放代理且未添加白名单，需用户名密码认证
username = "username"
password = "pwd"
proxy = fetch_one_proxy() # 获取一个代理

THRESHOLD = 2  # 换ip阈值
fail_time = 0  # 此ip异常次数

logger = logging.getLogger(__name__)


class TianyanchaSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TianyanchaDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        proxy_url = 'http://%s:%s@%s' % (username, password, proxy)
        request.meta['proxy'] = proxy_url  # 设置代理
        logger.debug("using proxy: {}".format(request.meta['proxy']))
        # 设置代理身份认证
        auth = "Basic %s" % (base64.b64encode(('%s:%s' % (username, password)).encode('utf-8'))).decode('utf-8')
        request.headers['Proxy-Authorization'] = auth

    def process_response(self, request, response, spider):
        """
            如果出现登录页，则增加ip异常次数
            当异常次数达到阈值, 则更换ip
        """
        global fail_time, proxy, THRESHOLD
        if re.match('.*login\?from=.*',response.url):
            fail_time += 1
            if fail_time >= THRESHOLD:
                proxy = fetch_one_proxy()
                fail_time = 0
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
