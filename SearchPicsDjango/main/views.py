from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import HttpResponse,JsonResponse

import psycopg2
import redis

from .db import DB

DB = DB()
SPIDERS = ['google', 'yandex', 'instagram']


def getKey(item):
    return item[2]


class SearchView(TemplateView):
    template_name = "search.html"

    def get(self, request, *args, **kwargs):
        #(kwargs['phrase'])
        id = DB.select(table_name="tasks", fields=["id"], keyword__contains=kwargs['phrase'])[0][0]
        pics = DB.select(table_name="results", id_task__e=id)
        pics = sorted(pics, key=getKey)
        return render(request, 'search.html', {'pics':pics})


class MainView(TemplateView):
    template_name = "index.html"

    def post(self, request, *args, **kwargs):
        r = redis.StrictRedis()
        value = request.POST.get('search')
        for spider in SPIDERS:
            query = "{}:start_urls".format(spider)
            r.lpush(query, value)
        try:
            tasks = DB.select(table_name="tasks")
        except:
            tasks = []
        return render(request, 'index.html',  {'tasks':tasks})

    def get(self, request, *args, **kwargs):
        try:
            tasks = DB.select(table_name="tasks")
        except:
            tasks=[]
        return render(request, 'index.html', {'tasks':tasks})


class TasksView(View):
    def get(self, request, *args, **kwargs):
        pics = DB.select(table_name="tasks")
        print(pics)
        res = {}
        for pic in pics:
            #print(pic[2])
            res[str(pic[2])] = str(pic[0])
        return JsonResponse(res)