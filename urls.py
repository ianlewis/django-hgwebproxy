# from django.conf.urls.defaults import *

# urlpatterns = patterns('',
#     # Example:
#     # (r'^hg/', include('hg.foo.urls')),

#     # Uncomment this for admin:
# #     (r'^admin/', include('django.contrib.admin.urls')),
# )

from django.conf.urls.defaults import *
from django.conf import settings
#from views import hgview
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^hg/login/$', 'django.contrib.auth.views.login', {'template_name':'registration/login.html'}, name='login'),
                       url(r'^hg/logout/$', 'django.contrib.auth.views.logout', {'template_name':'registration/logout.html'}, name='logout'),
                       #url(r'^hg/admin/', include('django.contrib.admin.urls')),
                       url(r'^hg/admin/(.*)', admin.site.root),
                       url(r'^hg/', include('hg.hgwebproxy.urls')),

                       )
