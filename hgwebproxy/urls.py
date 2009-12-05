from django.conf.urls.defaults import *

urlpatterns = patterns('hgwebproxy.views',
    #url('^$', 'repo_list', name='repo_list'),
    url('^(?P<slug>[\w-]+)/', 'repo_detail', name='repo_detail'),
)
