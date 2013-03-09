from django.conf.urls import patterns, url
from core import views

urlpatterns = patterns('',
    url(r'^projects/$', views.projects_all),
    url(r'^project/comment/new/$', views.add_comment, {}, 'comment-new'),
    url(r'^projects/search/$', views.search_projects2, {}, 'project-search'),
    url(r'^project/add/$', views.add_project),
    url(r'^project/add/image/$', views.add_project_image),
    url(r'^project/edit/(?P<pk>\d+)$', views.edit_project),

    url(r'^project/add/image/new/$', views.ImageProjectCreateView.as_view(), {}, 'upload-new'),
    url(r'^project/add/image/new/$', views.ImageProjectCreateView.as_view(), {}, 'upload-new'),
    url(r'^project/add/image/delete/(?P<pk>\d+)$', views.ImageProjectDeleteView.as_view(), {}, 'upload-delete'),
    url(r'^project/remove/(?P<pk>\d+)$', views.remove_project),

    url(r'^taggit_autosuggest/list/participant/$', views.get_participants),
    url(r'^taggit_autosuggest/list/location/$', views.get_locations),

    url(r'^list/location/$', views.get_locations),
    url(r'^list/(?P<tag>[^\.]+)/$', views.get_list),


    url(r'^comment/delete/(?P<pk>\d+)$', views.delete_comment, {}, 'comment-delete'),

    url(r'^project/(?P<slug>[^\.]+)/$', views.get_project, name="project_view"),
    url(r'^project/like/(?P<pk>\d+)$', views.like),
    url(r'^project/unlike/(?P<pk>\d+)$', views.unlike),


    url(r'^offers/$', views.offers_all),
    url(r'^offer/bookmark/(?P<state>[^\.]+)/(?P<pk>\d+)$', views.bookmark),
    url(r'^offers/search/$', views.search_offers, {}, 'offers-search'),
    url(r'^offer/posted_offers/$', views.posted_offers),
    url(r'^offer/apply/$', views.apply_offer),

    url(r'^offer/(?P<model>\w+)/$', views.edit_offer),
    url(r'^offer/(?P<model>\w+)/(?P<pk>\d+)/$', views.edit_offer),

    url(r'^offer/(?P<slug>[^\.]+)/$', views.get_offer, name="offer_view"),


    url(r'^profile/update/$', views.update_applicant, name="profile-update"),
    url(r'^profile/follow/(?P<pk>\d+)/$', views.follow),
    url(r'^profile/unfollow/(?P<pk>\d+)/$', views.unfollow),
    url(r'^profile/company/(?P<slug>[^\.]+)/$', views.get_company),
    url(r'^profile/school/(?P<slug>[^\.]+)/$', views.get_school),
    url(r'^profile/(?P<slug>[^\.]+)/followers/$', views.get_follow_profiles, {'type_url': 'followers'}),
    url(r'^profile/(?P<slug>[^\.]+)/following/$', views.get_follow_profiles, {'type_url': 'following'}),
    url(r'^profile/(?P<slug>[^\.]+)/$', views.get_applicant, name="profile_view"),
    url(r'^profile/$', views.get_my_profile),

    url(r'^education/add/$', views.add_education),
    url(r'^education/delete/(?P<pk>\d+)$', views.delete_education),
    url(r'^education/edit/(?P<pk>\d+)$', views.edit_education),
    url(r'^experience/add/$', views.add_experience),
    url(r'^experience/delete/(?P<pk>\d+)$', views.delete_experience),
    url(r'^experience/edit/(?P<pk>\d+)$', views.edit_experience),
    url(r'^$', views.home),
)
