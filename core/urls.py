from django.conf.urls import patterns, url
from core import views

urlpatterns = patterns('',
    url(r'^projects/$', views.projects),
    url(r'^project/add/$', views.add_project),
    url(r'^project/add/image/$', views.add_project_image),

    url(r'^project/add/image/new/$', views.ImageProjectCreateView.as_view(), {}, 'upload-new'),
    url(r'^project/add/image/delete/(?P<pk>\d+)$', views.ImageProjectDeleteView.as_view(), {}, 'upload-delete'),

    url(r'^project/(?P<slug>[^\.]+)/$', views.get_project),
    url(r'^offers/$', views.offers),
    url(r'^offer/add/$', views.add_offer),
    url(r'^offer/(?P<slug>[^\.]+)/$', views.get_offer),
    url(r'^profile/(?P<slug>[^\.]+)/$', views.get_applicant),
    url(r'^profile/company/(?P<slug>[^\.]+)/$', views.get_company),
    url(r'^profile/school/(?P<slug>[^\.]+)/$', views.get_school),
    url(r'^$', views.home),
)
