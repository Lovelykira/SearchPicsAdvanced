import scrapy
import random
from scrapy.shell import inspect_response
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.settings import Settings
from scrapy_redis.spiders import RedisSpider

import psycopg2

SEARCH = 'asd'
START = 10


class GoogleSpider(RedisSpider):
    name = "google"
    allowed_domains = ["google.com"]

    def __init__(self, search=""):
        super(GoogleSpider, self).__init__()
        self.search_phrase = search
        self.num_items = 5

    #    self.start_urls = (
    #            'https://www.google.com.ua/search?q=' + search + '&tbm=isch',
    #        )

        # if not self.check_search():
        #     self.start_urls = (
        #         'https://www.google.com.ua/search?q=' + search + '&tbm=isch',
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
    #         print "Check search errror"
    #         return False


    def parse(self, response):
        #inspect_response(response, self)
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
               print "ERROR KEY!", pic_link
            try:
                pic_img = link.split('src="')[1].split('</a>')[0]
                pic_img = pic_img.split('" width')[0]
            except:
                print "ERROR VAL!", pic_img
            yield {str(pic_link):str(pic_img)}


    def start_requests(self):
        for url in self.start_urls:
            headers = {}
            headers['User-Agent'] = str(random.randint(0,255))
#        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            yield scrapy.Request(url, headers=headers, dont_filter=True)


    def make_request_from_data(self, data):
        self.search_phrase = data
        if '://' in data:
            return self.make_requests_from_url(data)
        else:
            return self.make_requests_from_url('https://www.google.com.ua/search?q=' + data + '&tbm=isch')



