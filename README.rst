django-hgwebproxy
==============================

django-hgwebproxy is a django application which provides a version of mercurials
hgwebdir interface in which mercurial users and repositories can be managed
through Django's admin interface. Users are authenticated using django's auth
application and push/pull permissions can be assigned on a per-repository basis.

Requirements
-----------------------------

You will need django's auth module to use django-hgwebproxy. 'django.contrib.auth'
and it's dependencies must be installed in your django project.

Installation
-----------------------------

Installation can be done using easy_install or pip.::

    easy_install django-hgwebproxy

You can install the development version direcly from bitbucket as well::

    pip install -e hg+https://bitbucket.org/mariocesar/django-hgwebproxy/

After installing you will need to perform the following steps.

* Add 'hgwebproxy' to your INSTALLED_APPS
* Add hgwebproxy urls to urls.py::

    urlpatterns = patterns('',
        (r'^hg/', include('hgwebproxy.urls')),
    )

* Run syncdb::
  
    python manage.py syncdb

Testing
-----------------------------

Tests can be run without first creating a django project. Simply run tests
as you normally would for any python library. django-hgwebproxy's tests
set up the django environment for you::

    python setup.py test

AUTHORS
-----------------------

Authors in the order they were added to the file.

* Faheem Mitha <faheem@email.unc.edu>
* Jesper Noehr <jesper@noehr.org>
* Micah Ransdell
* Mario C&Atilde;&copy;sar Se&Atilde;&plusmn;oranis Ayala <mariocesar.sa@openit.com.bo>
* Ian Lewis <ianmlewis@gmail.com>
