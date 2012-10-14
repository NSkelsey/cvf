from django.conf.urls import patterns, include, url

from v0 import views


urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^posts/(?P<id_num>\d+)$', views.post_view),
    url(r'^posts/(?P<id_num>\d+)/sub_post$', views.sub_post),
    url(r'^make_post$', views.make_post),
    url(r'^login$', views.login),
)
