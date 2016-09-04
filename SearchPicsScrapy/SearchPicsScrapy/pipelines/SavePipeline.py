
import logging
import sys
import os
import redis
up = lambda x: os.path.dirname(x)
sys.path.insert(0, os.path.join(up(up(up(up(os.path.abspath(__file__))))), 'SearchPicsDjango'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SearchPicsDjango.settings")
import django
django.setup()
from main.models import Tasks, Results
from scrapy_djangoitem import DjangoItem


class TasksItem(DjangoItem):
    django_model = Tasks

class ResultsItem(DjangoItem):
    django_model = Results

class DBWriterPipeline(object):
    def __init__(self):
       # self.DB = DB()
        self.items_processed={'google':0,'yandex':0,'instagram':0}

    def process_item(self, item, spider):
        search_phrase = spider.search_phrase[-1]
        logging.log(logging.DEBUG, "Pipeline processing {} of {}. Item #{}".format(search_phrase, spider.search_phrase,
                                                                                self.items_processed))

        item = dict(item)
        # print("======================================")
        # for key, val in item.items():
        #     print(key, val)
        # print("======================================")
       # if 'error'in item.keys():
        #    return
        self.items_processed[spider.name] += 1
        if spider.user_pk != -1:
            task = TasksItem.django_model.objects.get(keyword=search_phrase, user_id=spider.user_pk)
        else:
            task = TasksItem.django_model.objects.get(keyword=search_phrase, user=None)
        if not 'error'in item.keys():
            for link, img in item.items():
                result = ResultsItem()
                result['task'] = task
                result['link'] = link
                result['img'] = img
                result['rank'] = self.items_processed[spider.name]
                result['site'] = spider.name
                result.save()
        if self.items_processed[spider.name] == spider.num_items or 'error'in item.keys():
            spider.search_phrase = spider.search_phrase[:-1]
            self.items_processed[spider.name] = 0
            cur_status = task.status.replace(" {}".format(spider.name), "")
            TasksItem.django_model.objects.filter(pk=task.pk).update(status=cur_status)
            logging.log(logging.DEBUG, "Pipeline processing {}. Status: {}".format(search_phrase, cur_status))
            if cur_status == "IN_PROGRESS":
                TasksItem.django_model.objects.filter(pk=task.pk).update(status="FINISHED")
                logging.log(logging.DEBUG, "Pipeline processing {}. FINISHED".format(search_phrase))
                run(search_phrase)
            else:
                TasksItem.django_model.objects.filter(pk=task.pk).update(status=cur_status.replace(" {}".format(spider.name), ""))

        return item


def run(search_phrase):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.publish('our-channel', search_phrase)
    logging.log(logging.DEBUG, "Pipeline sent message({}) to webserver".format(search_phrase))