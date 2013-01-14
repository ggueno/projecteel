from django.conf.urls import patterns, include, url
from core import views

urlpatterns = patterns('',
    url(r'^projects/$', views.projects),
    url(r'^project/(?P<slug>\w+)/$', views.get_project),
    url(r'^$', views.home),
)
