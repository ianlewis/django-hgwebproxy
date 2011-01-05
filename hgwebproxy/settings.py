import os
from django.conf import settings

STATIC_URL = getattr(settings, 'HGPROXY_STATIC_URL', os.path.join(settings.MEDIA_URL, 'hg/'))
TEMPLATE_PATHS = getattr(settings, 'HGPROXY_TEMPLATE_PATHS', None)

AUTH_REALM = getattr(settings, 'HGPROXY_AUTH_RELAM', 'Basic Auth')

STYLE = getattr(settings, 'HGPROXY_STYLE', 'coal')

REPO_PERMANENT_DELETE = getattr(settings, 'HGPROXY_REPO_PERMANENT_DELETE', False)

ALLOW_HTTP_PUSH = getattr(settings, 'HGPROXY_ALLOW_HTTP_PUSH', False)

# REPO_ROOT allows for rooting all repositories under a specific path.
REPO_ROOT = getattr(settings, 'HGPROXY_REPO_ROOT', None)

# REPO_PATH_CALLBACK is only used when the REPO_ROOT is set.
# If REPO_ROOT is set this callback accepts the repo model instance
# as an argument and returns the relative path from the REPO_ROOT.
# that resolve outsite the REPO_ROOT will cause errors in your application
# so inputs to your path must be checked beforehand for things like '..'.
REPO_PATH_CALLBACK = lambda repo: os.path.join(repo.owner.username, repo.slug)

# This is the REPO_ROOT used when running tests.
TEST_REPO_ROOT = getattr(settings, 'HGPROXY_TEST_REPO_ROOT', os.path.join(settings.MEDIA_ROOT, 'hg/'))
