# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
import time

from scrapy import signals
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from douban_users.units.proxy import GetIP


class DoubanUsersSpiderMiddleware(object):
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

        # Should return either None or an iterable of Request, dict
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


class DoubanUsersDownloaderMiddleware(object):
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
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
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


class DoubanTopicDownloaderMiddleware(object):
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
        with open("douban_users/cookies/request_cookies.txt", 'r') as fr:
            cookies = json.loads(fr.read())
        self.cookies = cookies

    def process_request(self, request, spider):
        if spider.name == 'topics' or 'topicitems':
            request.headers['User-Agent'] = self.user_agent
            request.cookies = self.cookies
            if 'rexxar/api/v2/gallery/topic' in request.url:
                topic_id = request.meta['topic_id']
                request.headers['Connection'] = 'keep-alive'
                request.headers['Content-Type'] = 'application/x-www-form-urlencoded'
                request.headers['Host'] = 'm.douban.com'
                request.headers['Origin'] = 'https://www.douban.com'
                request.headers['Referer'] = f'https://www.douban.com/gallery/topic/{topic_id}/?from=discussing'
                request.headers['Sec-Fetch-Mode'] = 'cors'
                request.headers['Sec-Fetch-Site'] = 'same-site'

class UserSeleniumDownloaderMiddleWare(object):
    def __init__(self):
        chrome_options = Options()
        # 设置headless模式
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # 设置不加载图片
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        self.browser = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options=chrome_options)
        with open("douban_users/cookies/cookies_selenium.txt", 'r') as fr:
            cookies = json.loads(fr.read())
        self.browser.get('https:www.douban.com')
        for cookie_dict in cookies:
            self.browser.add_cookie(cookie_dict)

    # def __del__(self):
    #     self.browser.close()

    def process_request(self, request, spider):
        if spider.name == 'topic_creators':
            self.browser.get(request.url)
            time.sleep(2)
            html = self.browser.page_source
            return HtmlResponse(url=self.browser.current_url, body=html, request=request, encoding='utf8')


class RandomProxyDownloaderMiddleware(object):
    #动态设置ip代理
    def process_request(self, request, spider):
        get_ip = GetIP()
        request.meta["proxy"] = get_ip.get_random_ip()