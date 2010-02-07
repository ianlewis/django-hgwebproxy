import os
import re

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _

from mercurial import commands,ui

import settings as hgproxy_settings

__all__ = (
    'create_repository',
    'delete_repository',
)

def create_repository(location):
    """
    Creates a new mercurial repository at the specified location
    if it doesn't exist already.

    Can throw IOErrors or OSErrors if there are any problems creating
    the repository on disk.
    """
    if re.match("[\w\d]+://", location):
        raise ValueError(_("Remote repository locations are not supported"))

    if not os.path.isabs(location):
        if not settings.REPO_ROOT:
            raise ImproperlyConfigured(_("REPO_ROOT must be defined in your settings file if using a relative path."))
        location = os.path.join(settings.REPO_ROOT, location)

    if not os.path.isdir(os.path.join(location, ".hg")):
        if not os.path.exists(location):
            os.mkdir(location)

        u = ui.ui()
        u.setconfig('ui', 'report_untrusted', 'off')
        u.setconfig('ui', 'interactive', 'off')
        commands.init(u, location)

def delete_repository(location):
    """
    Deletes the repository at the specified location if
    the REPO_PERMANENT_DELETE setting is True
    """
    if hgproxy_settings.REPO_PERMANENT_DELETE:
        import shutil
        shutil.rmtree(location)
