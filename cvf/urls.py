from django.conf.urls import patterns, include, url

from v0 import views


urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^posts/(?P<id_num>\d+)$', views.post_view),
    url(r'^posts/(?P<id_num>\d+)/sub_post$', views.sub_post),
    url(r'^posts/(?P<id_num>\d+)/vote$', views.vote),
    url(r'^posts/(?P<id_num>\d+)/rvote$', views.rel_vote),
    url(r'^make_post$', views.make_post),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^create$', views.create_user),
    url(r'^rvotes/update/(?P<username>\S+)$', views.reorder_rvotes),
    url(r'^user/(?P<username>\S+)$', views.profile),
)
