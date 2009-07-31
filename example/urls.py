from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/repos/', include('hgwebproxy.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name':'registration/login.html'}, name='login'),
   url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name':'registration/logout.html'}, name='logout'),
)

from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
