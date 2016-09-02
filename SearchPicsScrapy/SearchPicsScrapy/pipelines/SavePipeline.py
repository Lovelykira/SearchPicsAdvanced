#from .db import DB
import asyncio
import asyncio_redis
import sys
import os
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
        self.items_processed=0

   # def open_spider(self, spider):
    #    self.DB.create_table("tasks", id="SERIAL PRIMARY KEY", keyword="VARCHAR(500) NOT NULL", status="VARCHAR(500) NOT NULL")
     #   self.DB.create_table("results", id="SERIAL PRIMARY KEY", id_task="integer REFERENCES tasks (id)",
      #                       link="VARCHAR(2048) NOT NULL", img="VARCHAR(2048) NOT NULL",rank="integer NOT NULL",
     #                        site="VARCHAR(500) NOT NULL")

        #  if data != "":
        #  DB.insert(table_name="tasks", status="IN_PROGRESS", keyword=data)

    # def close_spider(self, spider):
    #     if self.DB.con:
    #         self.DB.con.close()

    def process_item(self, item, spider):
        if item == "Parse error":
            return
        self.items_processed += 1
        item = dict(item)

        if spider.user_pk != -1:
            task = TasksItem.django_model.objects.get(keyword=spider.search_phrase, user_id=spider.user_pk)
        else:
            task = TasksItem.django_model.objects.get(keyword=spider.search_phrase, user=None)
        for link, img in item.items():
            result = ResultsItem()
            result['task'] = task
            result['link'] = link
            result['img'] = img
            result['rank'] = self.items_processed
            result['site'] = spider.name
            result = result.save()
        if self.items_processed == spider.num_items:
            self.items_processed = 0
            cur_status = task.status
            TasksItem.django_model.objects.filter(pk=task.pk).update(status=cur_status.replace(" {}".format(spider.name), ""))
            if task.status == "IN_PROGRESS":
                TasksItem.django_model.objects.filter(pk=task.pk).update(status="FINISHED")
                run("OK")


            #Results.objects.create(task_pk=task_id, link=link, img=img, rank=self.items_processed, site=spider.name )

         # if self.items_processed==0 and spider.search_phrase != "":
         #     task_id = self.DB.select(table_name="tasks", fields=['id', 'status'], keyword__contains=spider.search_phrase)
         #     if task_id == []:
         #        self.task_id = self.DB.insert(table_name="tasks", status="IN_PROGRESS yandex google instagram", keyword=spider.search_phrase, returning_id=True)[0]
         #     elif task_id[0][1] == "FINISHED":
         #         return item
         #     else:
         #         self.task_id = task_id[0][0]
         # for key,val in item.items():
         #     self.i = self.i+1
         #    # id = self.DB.select(table_name="tasks", fields=['id'], keyword__contains=spider.search_phrase)
         #     self.DB.insert(table_name="results", id_task=self.task_id, link=key, img=val, rank=self.i, site=spider.name)
         #     if self.i == spider.num_items:
         #         self.i=0
         #         status = self.DB.select(table_name="tasks", fields=['status'], keyword__contains=spider.search_phrase)
         #         status = status[0][0].replace(" {}".format(spider.name), "")
         #         if status == "IN_PROGRESS":
         #             status = "FINISHED"
         #         self.DB.update(table_name="tasks", set_status=status, keyword__contains=spider.search_phrase)


            # self.DB.insert(table_name="tasks", returning_id=False, keyword=spider.search_phrase, status="'IN_PROGRESS'")
            # self.DB.update(table_name="tasks", set_status="GOOD", id__lt=20, returning=["keyword"])
            # self.DB.select(table_name="tasks")
        return item


loop = asyncio.get_event_loop()


def run(text):
    # Create a new redis connection (this will also auto reconnect)
    connection = yield from asyncio_redis.Connection.create('localhost', 6379)

    try:
            # Publish value
            try:
                yield from connection.publish('spider-channel', text)
                print('Published.')
            except asyncio_redis.Error as e:
                print('Published failed', repr(e))

    finally:
        connection.close()

