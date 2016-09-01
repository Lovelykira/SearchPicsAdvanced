from __future__ import absolute_import
from celery import shared_task, task
from .SearchPicsScrapy.SearchPicsScrapy.spiders import google_spider
from celery.signals import worker_process_init
from multiprocessing import current_process


@task.task
def start_google_spider(link):
    google_spider.google_crawl(link)


@worker_process_init.connect
def fix_multiprocessing(**kwargs):
    try:
        current_process()._config
    except AttributeError:
        current_process()._config = {'semprefix': '/mp'}
