from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import settings

from hitcount.views import update_hit_count_ajax

import notifications


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'', include('core.urls')),
    url(r'^ajax/hit/$', # you can change this url if you would like
        update_hit_count_ajax,
        name='hitcount_update_ajax'), # keep this name the same

    # url(r'^$', 'projecteel.views.home', name='home'),
    # url(r'^projecteel/', include('projecteel.foo.urls')),
    (r'^accounts/', include('registration.urls')),
    (r'^grappelli/', include('grappelli.urls')), url(r'^admin/', include(admin.site.urls)),
    (r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':  settings.MEDIA_ROOT}),
    (r'^tinymce/', include('tinymce.urls')),
    (r'^elsewhere/', include('elsewhere.urls')),
    (r'^inbox/notifications/', include('notifications.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}),
    )
