from django.shortcuts import render
from django.views.generic import TemplateView, View, FormView
from django.http import HttpResponse,JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin

import psycopg2
import redis

from .models import Results, Tasks
from .forms import LoginForm, RegistrationForm

from .db import DB

#DB = DB()
SPIDERS = ['google', 'yandex', 'instagram']


def getKey(item):
    return item.rank


class SearchView(TemplateView):
    template_name = "search.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            task = Tasks.objects.filter(keyword=kwargs['phrase'], user=request.user)
        else:
            task = Tasks.objects.filter(keyword=kwargs['phrase'], user=None)
        pics = Results.objects.filter(task=task)
        pics = sorted(pics, key=getKey)
        #(kwargs['phrase'])
        #id = Tasks.objects.filter(keyword=kwargs['phrase'])
        #id = DB.select(table_name="tasks", fields=["id"], keyword__contains=kwargs['phrase'])[0][0]
        #pics = DB.select(table_name="results", id_task__e=id)
        #pics = sorted(pics, key=getKey)
        return render(request, 'search.html', {'pics':pics})


class MainView(TemplateView):
    template_name = "index.html"

    def post(self, request, *args, **kwargs):
        value = request.POST.get('search')
        if "||" in value:
            value.replace("||", "")
        if request.user.is_authenticated():
            task, created = Tasks.objects.get_or_create(keyword=value, user=request.user)
            if created:
                task.status = "IN_PROGRESS yandex google instagram"
                task.save()
                value += '||{}'.format(request.user.pk)
                for spider in SPIDERS:
                    query = "{}:start_urls".format(spider)
                    r = redis.StrictRedis()
                    r.lpush(query, value)
        else:
            task, created = Tasks.objects.get_or_create(user=None)
            if task.keyword == value:
                return HttpResponseRedirect('/search/' + value)
            task.status = "IN_PROGRESS yandex google instagram"
            task.keyword = value
            task.save()
            anonymous_res = Results.objects.filter(task=task).delete()
            for spider in SPIDERS:
                query = "{}:start_urls".format(spider)
                r = redis.StrictRedis()
                r.lpush(query, value)

        if request.user.is_authenticated():
            tasks = Tasks.objects.filter(user=request.user.pk)
            return render(request, 'index.html', {'tasks': tasks})
        else:
            return HttpResponseRedirect('/search/'+value)
        # try:
        #     tasks = DB.select(table_name="tasks")
        # except:
        #     tasks = []


    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            tasks = Tasks.objects.filter(user=request.user.pk)
        else:
            tasks = []
            # try:
            #     tasks = DB.select(table_name="tasks")
            # except:
            #     tasks=[]
        return render(request, 'index.html', {'tasks':tasks})


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def form_valid(self, form):
        #user = form.save()
        user = form.get_authenticated_user()
        login(self.request, user)
        return HttpResponseRedirect('/')


class LogoutView(View, LoginRequiredMixin):
    redirect_field_name = '/login/'
    def get(self, request):
        logout(self.request)
        return HttpResponseRedirect('/')


class RegisterView(FormView):
    form_class = RegistrationForm
    template_name = 'register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect('/')



class TasksView(View):
    def get(self, request, *args, **kwargs):
        res={}
        # pics = DB.select(table_name="tasks")
        # print(pics)
        # res = {}
        # for pic in pics:
        #     #print(pic[2])
        #     res[str(pic[2])] = str(pic[0])
        return JsonResponse(res)


