import scrapy
import psycopg2
import random
import logging
import json

from fake_useragent import UserAgent

from scrapy_redis.spiders import RedisSpider

class YandexSpider(RedisSpider):
    """
    Class YandexSpider searches the results in instagram.ua
    """
    name = "yandex"
    allowed_domains = ["yandex.ua"]
    # user_agents = ['Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
    #                'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0',
    #                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    #                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
    #                ]

    def __init__(self, search=""):
        super(YandexSpider, self).__init__()
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
            images_list = response.xpath(".//div[@class='page-layout__column page-layout__column_type_content']")[0]
            images_list = images_list.xpath(".//div[@class='page-layout__content-wrapper b-page__content']")[0]
            images_list = images_list.xpath(".//div[@class='serp-controller__content']")[0]
            links = images_list.xpath(".//a[@class='serp-item__link']")[:self.num_items]
            for link in links:
                img = link.xpath("./img")
                pic_link = 0
                pic_img = 0
                try:
                    link = link.extract()
                    pic_link = link.split('href="')[1]
                    pic_link = pic_link.split('">')[0]
                    pic_link = 'https://yandex.ua'+pic_link
                except:
                   logging.log(logging.ERROR, "Spider {} couldn't parse the pic's link".format(self.name))
                try:
                    img = img.extract()[0]
                    pic_img = img.split('src="')[1]
                    pic_img = pic_img.split('" onerror=')[0]
                except:
                    logging.log(logging.ERROR, "Spider {} couldn't parse the pic's img".format(self.name))
                logging.log(logging.DEBUG, "Spider {} proceeded {}".format(self.name, {str(pic_link): str(pic_img)}))
                yield {str(pic_link): str(pic_img)}
        except:
            logging.log(logging.ERROR, "Spider {} couldn't parse the page".format(self.name))
            yield {'error': True}

    # def start_requests(self):
    #     for url in self.start_urls:
    #         ua = UserAgent()
    #         headers = {}
    #         headers['User-Agent'] =  ua.random
    #         yield scrapy.Request(url, headers=headers, dont_filter=True)
          #  headers = {}
          #  headers['User-Agent'] = str(random.randint(0,255))
#        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            #yield scrapy.Request(url, headers=headers, dont_filter=True)


    def make_request_from_data(self, data):
        """
        The method that analyzes data from redis list.

        It splits the data into search phrase and user pk and stores this variables in spider's fields.
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

        return self.make_requests_from_url('https://yandex.ua/images/search?text=' + data)


