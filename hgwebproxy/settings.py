import os
from django.conf import settings

STATIC_URL = getattr(settings, 'HGPROXY_STATIC_URL', os.path.join(settings.MEDIA_URL, 'hg/'))
TEMPLATE_PATH = getattr(settings, 'HGPROXY_TEMPLATE_PATH', None)

AUTH_REALM = getattr(settings, 'HGPROXY_AUTH_RELAM', 'Basic Auth')
