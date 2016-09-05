import scrapy
import random
from scrapy.shell import inspect_response
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.settings import Settings
from scrapy_redis.spiders import RedisSpider
from fake_useragent import UserAgent
import logging

import psycopg2
import json

SEARCH = 'asd'
START = 10


class GoogleSpider(RedisSpider):
    """
    Class GoogleSpider searches the results in google.com.ua
    """
    name = "google"
    allowed_domains = ["google.com"]

    def __init__(self, search=""):
        super(GoogleSpider, self).__init__()
        self.search_phrase = []
        self.num_items = 10
        self.user_pk = -1


    def parse(self, response):
        """
        The method that parses the response page.

        @param response:
        @return: if everything is ok, it returns dict with picture's image link as key and pictures image source as value.
        if not it returns dict with 'error' as key.
        """
        #inspect_response(response, self)
        try:
            images_table = response.xpath(".//table[@class='images_table']")[0]
            links = images_table.xpath(".//td")[:self.num_items]
            for link in links:
                link = link.xpath('./a')[0].extract()
                pic_link = 0
                pic_img = 0
                try:
                    pic_link = link.split('href="')[1]
                    pic_link = pic_link.split('"><')[0]
                    pic_link = 'https://google.com.ua'+pic_link
                except:
                    logging.log(logging.ERROR, "Spider {} couldn't parse the pic's link".format(self.name))
                try:
                    pic_img = link.split('src="')[1].split('</a>')[0]
                    pic_img = pic_img.split('" width')[0]
                except:
                    logging.log(logging.ERROR, "Spider {} couldn't parse the pic's img".format(self.name))
                logging.log(logging.DEBUG, "Spider {} proceeded {}".format(self.name, {str(pic_link): str(pic_img)}))
                yield {str(pic_link):str(pic_img)}
        except:
            logging.log(logging.ERROR, "Spider {} couldn't parse the page".format(self.name))
            yield {'error': True}


    # def start_requests(self):
    #     for url in self.start_urls:
    #         ua = UserAgent()
    #         headers = {}
    #         headers['User-Agent'] = ua.random
    #         yield scrapy.Request(url, headers=headers, dont_filter=True)


    def make_request_from_data(self, data):
        """
        The method that analyzes data from redis list.

        It splits the data into search phrase and user pk and stores this variables in spider's fields.
        @param data: str.
        @return: calls make_requests_from_url method.
        """
        data_json = json.loads(data)
        data = data_json['value']
        if data_json['user']:
            self.user_pk = data_json['user']
        else:
            self.user_pk = -1
        # if "||" in data:
        #     data, user_pk = data.split("||")
        #     self.user_pk = user_pk
        # else:
        #     self.user_pk = -1
        self.search_phrase.append(data)

        return self.make_requests_from_url('https://www.google.com.ua/search?q=' + data + '&tbm=isch')