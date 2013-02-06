from django.conf.urls import patterns, url
from core import views

urlpatterns = patterns('',
    url(r'^projects/$', views.projects_all),
    url(r'^projects/search/$', views.search_projects2),
    url(r'^project/add/$', views.add_project),
    url(r'^project/add/image/$', views.add_project_image),

    url(r'^project/add/image/new/$', views.ImageProjectCreateView.as_view(), {}, 'upload-new'),
    url(r'^project/add/image/delete/(?P<pk>\d+)$', views.ImageProjectDeleteView.as_view(), {}, 'upload-delete'),
    url(r'^project/remove/(?P<pk>\d+)$', views.remove_project),
    url(r'^locations/list/$', views.get_locations),
    url(r'^tags/list/$', views.get_tags),
    url(r'^skills/list/$', views.get_tags),
    url(r'^list/(?P<tag>[^\.]+)/$', views.get_list),


    url(r'^comment/delete/(?P<pk>\d+)$', views.delete_comment, {}, 'comment-delete'),

    url(r'^project/(?P<slug>[^\.]+)/$', views.get_project, name="project_view"),
    url(r'^project/like/(?P<pk>\d+)$', views.like),
    url(r'^project/comment/new/$', views.add_comment, {}, 'comment-new'),


    url(r'^offers/$', views.offers),
    url(r'^offer/add/$', views.add_offer),
    url(r'^offer/posted_offers/$', views.posted_offers),
    url(r'^offer/(?P<slug>[^\.]+)/$', views.get_offer, name="offer_view"),
    url(r'^offer/apply/(?P<pk>\d+)$', views.apply_offer),


    url(r'^profile/follow/(?P<pk>\d+)/$', views.follow),
    url(r'^profile/unfollow/(?P<pk>\d+)/$', views.unfollow),
    url(r'^profile/company/(?P<slug>[^\.]+)/$', views.get_company),
    url(r'^profile/school/(?P<slug>[^\.]+)/$', views.get_school),
    url(r'^profile/(?P<slug>[^\.]+)/$', views.get_applicant, name="profile_view"),
    url(r'^profile/$', views.get_my_profile),

    url(r'^education/add/$', views.add_education),
    url(r'^education/delete/(?P<pk>\d+)$', views.delete_education),
    url(r'^experience/add/$', views.add_experience),
    url(r'^experience/delete/(?P<pk>\d+)$', views.delete_experience),
    url(r'^$', views.home),
)
