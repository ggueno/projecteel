from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import settings
<<<<<<< HEAD
=======

>>>>>>> 40fa773b79d55b248e5285b82151dbd47238c48c
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'', include('core.urls')),
    # url(r'^$', 'projecteel.views.home', name='home'),
    # url(r'^projecteel/', include('projecteel.foo.urls')),
    (r'^accounts/', include('registration.urls')),
    (r'^grappelli/', include('grappelli.urls')), url(r'^admin/', include(admin.site.urls)),
    (r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
<<<<<<< HEAD
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':  settings.MEDIA_ROOT}),

=======
    
>>>>>>> 40fa773b79d55b248e5285b82151dbd47238c48c
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
<<<<<<< HEAD
=======

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}),
    )

>>>>>>> 40fa773b79d55b248e5285b82151dbd47238c48c
