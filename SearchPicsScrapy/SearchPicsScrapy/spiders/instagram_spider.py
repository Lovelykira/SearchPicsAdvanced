import scrapy
import psycopg2
import random
import json
from scrapy.shell import inspect_response
from fake_useragent import UserAgent
import re

from scrapy_redis.spiders import RedisSpider


class InstagramSpider(RedisSpider):
    name = "instagram"
    allowed_domains = ["instagram.com"]

    def __init__(self, search=""):
        super(InstagramSpider, self).__init__()
        self.search_phrase = search
        self.num_items = 5
        self.user_pk = -1

       # self.start_urls = (
       #     'https://www.instagram.com/explore/tags/' + search + '/?__a=1',
       # )

        # if not self.check_search():
        #     self.start_urls = (
        #         'https://yandex.ua/images/search?text='+search,
        #     )
        # else:
        #     self.start_urls =()

    # def check_search(self):
    #     try:
    #         con = psycopg2.connect(database='spiderdb', user='kira')
    #         cur = con.cursor()
    #         cur.execute("SELECT * FROM search_query;")
    #         search_query = cur.fetchall()
    #         for item in search_query:
    #             if item[1] == self.search_phrase:
    #                 return True
    #         return False
    #
    #     except:
    #         print("Check search errror")
    #         return False


    def parse(self, response):
        pic_link = 'https://www.instagram.com/explore/tags/' + self.search_phrase
        try:
            data = response.xpath("body").xpath("p").extract()
            images_list = data[0].split('display_src": "')[1:self.num_items+1]
            for image in images_list:
                pic_img = image.split('"}')[0]
                pic_img = str(pic_img)
                yield {pic_link: pic_img}
        except:
            print "Parse error"
            yield "Parse error"


    def start_requests(self):
        for url in self.start_urls:
            ua = UserAgent()
            headers = {}
            headers['User-Agent'] = ua.random
            yield scrapy.Request(url, headers=headers, dont_filter=True)
            #headers = {}
            #headers['User-Agent'] = str(random.randint(0,255))
#        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            #yield scrapy.Request(url, headers=headers, dont_filter=True)


    def make_request_from_data(self, data):
        if "||" in data:
            data, user_pk = data.split("||")
            self.user_pk = user_pk
        self.search_phrase = data
        if " "  in data:
            data = data.replace(" ", "_")
        # for char in data:
        #     print(char)
        #     if char not in r'[A-Za-z0-9]':
        #         data = data.replace(char, "")
        if '://' in data:
            return self.make_requests_from_url(data)
        else:
            return self.make_requests_from_url('https://www.instagram.com/explore/tags/' + data + '/?__a=1')


