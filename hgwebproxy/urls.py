from django.conf.urls.defaults import *

urlpatterns = patterns('hg.hgwebproxy.views',
    url(r'^(.*)', 'hgroot', name='hgroot'),
)
