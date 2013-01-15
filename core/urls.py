from django.conf.urls import patterns, include, url
from core import views

urlpatterns = patterns('',
    url(r'^projects/$', views.projects),
    url(r'^project/add/$', views.add_project),
    url(r'^project/(?P<slug>[^\.]+)/$', views.get_project),
    url(r'^offers/$', views.offers),
    url(r'^offer/add/$', views.add_offer),
    url(r'^offer/(?P<slug>[^\.]+)/$', views.get_offer),
    url(r'^$', views.home),
)
