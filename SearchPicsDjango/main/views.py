from django.shortcuts import render
from django.views.generic import TemplateView, View, FormView
from django.http import HttpResponse,JsonResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin

import re
import psycopg2
import redis
import time

from datetime import datetime, timedelta

from .models import Results, Tasks
from .forms import LoginForm, RegistrationForm

import logging
logger = logging.getLogger(__name__)

SPIDERS = ['google', 'yandex', 'instagram']


def byRank(item):
    return item.rank

def byID(item):
    return item.id


class SearchView(TemplateView):
    template_name = "search.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            task = Tasks.objects.filter(keyword=kwargs['phrase'], user=request.user)
        else:
            task = Tasks.objects.filter(keyword=kwargs['phrase'], user=None)
        pics = Results.objects.filter(task=task)
        pics = sorted(pics, key=byRank)
        return render(request, 'search.html', {'pics':pics})


class MainView(TemplateView):
    template_name = "index.html"

    def spiders_search(self, value):
        for spider in SPIDERS:
            query = "{}:start_urls".format(spider)
            r = redis.StrictRedis()
            r.lpush(query, value)

    def get_finished_tasks(self, user, **kwargs):
        if user:
            tasks = Tasks.objects.filter(user_id=user.id, status="FINISHED")
            return sorted(tasks, key=byID)
        else:
            tasks = Tasks.objects.filter(user=user, status="FINISHED")
            return sorted(tasks, key=byID)

    def get_in_progress_tasks(self, user, **kwargs):
        if user:
            tasks = Tasks.objects.filter(user_id=user.id).exclude(status="FINISHED")
            return sorted(tasks, key=byID)
        else:
            tasks = Tasks.objects.filter(user=user).exclude(status="FINISHED")
            return sorted(tasks, key=byID)

    def save_task(self, task, value):
        task.status = "IN_PROGRESS yandex google instagram"
        task.keyword = value
        task.save()

    def normalize_value(self, value):
        q = re.compile(r'[^a-zA-Z0-9_ ]')
        return q.sub('', value)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            user = request.user
        else:
            user = None
        value = self.normalize_value(request.POST.get('search', ""))
        finished_tasks = self.get_finished_tasks(user)
        if value == "":
            return render(request, 'index.html', {'tasks': finished_tasks})
        if user:
            task, created = Tasks.objects.get_or_create(keyword=value, user=user)
            one_day = timedelta(days=1)
            if created or task.date + one_day < datetime.date(datetime.now()):
                self.save_task(task, value)
                value += '||{}'.format(user.pk)
                self.spiders_search(value)
        else:
            task, _ = Tasks.objects.get_or_create(user=user)
            Results.objects.filter(task=task).delete()
            self.save_task(task, value)
            self.spiders_search(value)

        finished_tasks = self.get_finished_tasks(user)
        in_progress_tasks = self.get_in_progress_tasks(user)
        return render(request, 'index.html', {'tasks': finished_tasks, 'tasks2':in_progress_tasks})

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            user = request.user
        else:
            user = None
        finished_tasks = self.get_finished_tasks(user)
        in_progress_tasks = self.get_in_progress_tasks(user)
        return render(request, 'index.html', {'tasks':finished_tasks, 'tasks2':in_progress_tasks})



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


