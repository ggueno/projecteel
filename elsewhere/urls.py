from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('elsewhere.views',
    url(r'^$', 'elsewhere', name='elsewhere'),
)
