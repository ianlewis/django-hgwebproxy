#!/usr/bin/python

import os, sys
import django.core.handlers.wsgi

"""
The directory added to sys.path would be the directory containing the
package for the Django site created by running:

django-admin.py startproject mysite

If you have been using the Django development server and have made
use of the fact that it is possible when doing explicit imports, or
when referencing modules in 'urls.py', to leave out the name of the
site and use a relative module path, you will also need to add to
sys.path the path to the site package itself.

sys.path.append('/usr/local/django')
sys.path.append('/usr/local/django/mysite')
"""

sys.path.append('/var/django')
os.environ['DJANGO_SETTINGS_MODULE'] = 'hg.settings'
application = django.core.handlers.wsgi.WSGIHandler()


