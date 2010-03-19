#:coding=utf-8:
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('hgwebproxy.views',
    url('^$', 'repo_list', name='repo_list'),
)

if settings.DEBUG:
    urlpatterns += patterns('hgwebproxy.views',
        url('^static/(?P<file_name>.+)$', 'static_file', name='repo_static_file'),
    )

urlpatterns += patterns('hgwebproxy.views', 
    url('^(?P<pattern>.+)', 'repo_detail', name='repo_detail'),
)

