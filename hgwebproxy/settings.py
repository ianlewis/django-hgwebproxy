import os
from django.conf import settings

STATIC_URL = getattr(settings, 'HGPROXY_STATIC_URL', os.path.join(settings.MEDIA_URL, 'hg/'))
TEMPLATE_PATHS = getattr(settings, 'HGPROXY_TEMPLATE_PATHS', None)

AUTH_REALM = getattr(settings, 'HGPROXY_AUTH_RELAM', 'Basic Auth')

STYLE = getattr(settings, 'HGPROXY_STYLE', 'coal')

REPO_LIST_REQUIRES_LOGIN = getattr(settings, 'HGPROXY_REPO_LIST_REQUIRES_LOGIN', False)

REPO_PERMANENT_DELETE = getattr(settings, 'HGPROXY_REPO_PERMANENT_DELETE', False)
