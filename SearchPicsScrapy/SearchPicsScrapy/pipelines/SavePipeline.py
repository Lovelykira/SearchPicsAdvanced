#from .db import DB
import sys
import os
sys.path.insert(0, "/home/kira/PycharmProjects/SearchPicsAdvanced/SearchPicsDjango")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SearchPicsDjango.settings")
from SearchPicsDjango 
from scrapy_djangoitem import DjangoItem
#from django.db.models import F

class TasksItem(DjangoItem):
    django_model = main.models.Tasks

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
        self.items_processed += 1
        item = dict(item)
        task = Tasks.objects.filter(keyword=spider.search_phrase, user_pk=spider.user_pk)
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
            task.update(status=cur_status.replace(" {}".format(spider.name), ""))
            if task.status == "IN_PROGRESS":
                task.update(status="FINISHED")

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
