from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'tasks/$', TasksView.as_view()),
    url(r'search/(?P<phrase>\w+)/$', SearchView.as_view()),
    url(r'^$', MainView.as_view()),
    url(r'^login/$', LoginView.as_view()),
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^register/$', RegisterView.as_view())
]