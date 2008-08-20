from django.conf.urls.defaults import *

urlpatterns = patterns('hgwebproxy.views',
    url(r'^(.*)', 'hgroot', name='hgroot'),
)
