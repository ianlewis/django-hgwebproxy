from django.conf.urls.defaults import *

urlpatterns = patterns('hgwebproxy.views',
    url('^$', 'repo_list', name='repo_list'),
    url('^(?P<slug>[\w-]+)/', 'repo', name='repo_detail'),
)
