from django.conf.urls.defaults import *

urlpatterns = patterns('cx.apps.hgwebproxy.views',
    url(r'^(.*)', 'hgroot', name='hgroot'),
)