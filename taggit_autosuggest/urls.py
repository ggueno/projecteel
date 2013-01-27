from django.conf.urls.defaults import *


urlpatterns = patterns('taggit_autosuggest.views',
    url(r'^list/(?P<tagName>.*)/$', 'list_tags', name='taggit_autosuggest-list-tag'),
    url(r'^list/$', 'list_tags', name='taggit_autosuggest-list'),
)
