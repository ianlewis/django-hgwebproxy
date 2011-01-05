#:coding=utf-8:

import os

from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from django.conf import settings

from hgwebproxy.tests.base import RepoTestCase, RequestTestCaseMixin
from hgwebproxy import settings as hgwebproxy_settings

class HgWebTest(RequestTestCaseMixin, RepoTestCase):

    def test_hgwebdir_top(self):
        response = self.client.get(reverse("repo_list"))
        self.assertOk(response)
        self.assertHtml(response)

    def test_repo_detail(self):
        self.client.login(username="owner", password="owner")

        response = self.client.get(reverse('repo_detail',  kwargs={'pattern':'test-repo/'}))
        self.assertOk(response)
        self.assertHtml(response)

    def test_repo_detail_forbidden(self):
        self.client.login(username="no_perms", password="no_perms")
        response = self.client.get(reverse('repo_detail',  kwargs={'pattern':'test-repo/'}))
        self.assertForbidden(response)

class DebugStaticFilesTest(RequestTestCaseMixin, RepoTestCase):

    def setUp(self):
        super(DebugStaticFilesTest, self).setUp()
        self.old_debug = settings.DEBUG
        settings.DEBUG = True

    def tearDown(self):
        super(DebugStaticFilesTest, self).tearDown()
        settings.DEBUG = self.old_debug

    def _get_environ(self, path, data={}):
        import urllib
        from urlparse import urlparse, urlunparse, urlsplit
        from django.test.client import FakePayload

        parsed = urlparse(path)
        r = {
            'CONTENT_TYPE':    'text/html; charset=utf-8',
            'PATH_INFO':       urllib.unquote(parsed[2]),
            'QUERY_STRING':    urlencode(data, doseq=True) or parsed[4],
            'REQUEST_METHOD': 'GET',
            'wsgi.input':      FakePayload('')
        }
        environ = {
            'HTTP_COOKIE':       self.client.cookies.output(header='', sep='; '),
            'PATH_INFO':         '/',
            'QUERY_STRING':      '',
            'REMOTE_ADDR':       '127.0.0.1',
            'REQUEST_METHOD':    'GET',
            'SCRIPT_NAME':       '',
            'SERVER_NAME':       'testserver',
            'SERVER_PORT':       '80',
            'SERVER_PROTOCOL':   'HTTP/1.1',
            'wsgi.version':      (1,0),
            'wsgi.url_scheme':   'http',
            'wsgi.errors':       self.client.errors,
            'wsgi.multiprocess': True,
            'wsgi.multithread':  False,
            'wsgi.run_once':     False,
        }
        environ.update(r)
        return environ

    def test_static_file(self):
        from django.core.handlers.wsgi import WSGIRequest
        from hgwebproxy.views import static_file

        request = WSGIRequest(self._get_environ('/hg/static/hglogo.png'))
        response = static_file(request, 'hglogo.png')
        self.assertOk(response)
        self.assertHeader(response, "Content-Type", "image/png")
