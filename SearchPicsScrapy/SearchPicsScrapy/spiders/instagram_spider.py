import scrapy
import psycopg2
import random
import json
from scrapy.shell import inspect_response
from fake_useragent import UserAgent
import re
import logging

from scrapy_redis.spiders import RedisSpider


class InstagramSpider(RedisSpider):
    """
    Class InstagramSpider searches the results in instagram.com
    """
    name = "instagram"
    allowed_domains = ["instagram.com"]

    def __init__(self, search=""):
        super(InstagramSpider, self).__init__()
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
        pic_link = 'https://www.instagram.com/explore/tags/' + self.search_phrase[0]
        try:
            data = response.xpath("body").xpath("p").extract()
            images_list = data[0].split('display_src": "')[1:self.num_items+1]
            for image in images_list:
                pic_img = image.split('"}')[0]
                pic_img = str(pic_img)
                yield {pic_link: pic_img}
        except:
            logging.log(logging.ERROR, "Spider {} couldn't parse the page".format(self.name))
            yield {'error': True}


    # def start_requests(self):
    #     for url in self.start_urls:
    #         ua = UserAgent()
    #         headers = {}
    #         headers['User-Agent'] = ua.random
    #         yield scrapy.Request(url, headers=headers, dont_filter=True)
            #headers = {}
            #headers['User-Agent'] = str(random.randint(0,255))
#        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            #yield scrapy.Request(url, headers=headers, dont_filter=True)


    def make_request_from_data(self, data):
        """
        The method that analyzes data from redis list.

        It splits the data into search phrase and user pk and stores this variables in spider's fields.
        If data contains spaces, it would be replaced by _.
        @param data:
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
        if " "  in data:
            data = data.replace(" ", "_")
        return self.make_requests_from_url('https://www.instagram.com/explore/tags/' + data + '/?__a=1')


