import scrapy
import psycopg2
import random

from fake_useragent import UserAgent

from scrapy_redis.spiders import RedisSpider

class YandexSpider(RedisSpider):
    name = "yandex"
    allowed_domains = ["yandex.ua"]
    user_agents = ['Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0',
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
                   ]

    def __init__(self, search=""):
        super(YandexSpider, self).__init__()
        self.search_phrase = search
        self.num_items = 5
        self.user_pk = -1

       # self.start_urls = (
       #     'https://yandex.ua/images/search?text=' + search,
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
        print("PARSE")
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
                    print(pic_link)
                    pic_link = pic_link.split('">')[0]
                    pic_link = 'https://yandex.ua'+pic_link
                except:
                   print("ERROR KEY!", pic_link)
                try:
                    img = img.extract()[0]
                    pic_img = img.split('src="')[1]
                    print("pic_img")
                    pic_img = pic_img.split('" onerror=')[0]
                except:
                    print("ERROR VAL!", pic_img)
                yield {str(pic_link): str(pic_img)}
        except:
            print("Yandex showed capcha")
            yield "Parse error"


    def start_requests(self):
        for url in self.start_urls:
            ua = UserAgent()
            headers = {}
            headers['User-Agent'] =  ua.random
            yield scrapy.Request(url, headers=headers, dont_filter=True)
          #  headers = {}
          #  headers['User-Agent'] = str(random.randint(0,255))
#        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            #yield scrapy.Request(url, headers=headers, dont_filter=True)


    def make_request_from_data(self, data):
        if "||" in data:
            data, user_pk = data.split("||")
            self.user_pk = user_pk
        self.search_phrase = data

        if '://' in data:
            return self.make_requests_from_url(data)
        else:
            return self.make_requests_from_url('https://yandex.ua/images/search?text=' + data)


