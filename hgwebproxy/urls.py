from django.conf.urls.defaults import *

urlpatterns = patterns('hg.hgwebproxy.views',
    url(r'^repo_dir(.*)', 'hgroot', name='hgwebdir'),
    url(r'^repo/(?P<slug>[-\w]+)', 'hgweb',),
)
