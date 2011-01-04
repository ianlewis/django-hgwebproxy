#:coding=utf-8:

import os

from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from hgwebproxy.tests.base import RepoTestCase
from hgwebproxy import settings as hgwebproxy_settings

class RequestTestCaseMixin(object):

    def assertStatus(self, response, status=200):
        self.assertEquals(response.status_code, status)

    def assertOk(self, response):
        self.assertStatus(response)

    def assertBadRequest(self, response):
        self.assertStatus(response, 400)

    def assertForbidden(self, response):
        self.assertStatus(response, 403)

    def assertNotFound(self, response):
        self.assertStatus(response, 404)

    def assertRedirect(self, response, redirect_url=None):
        self.assertStatus(response, 302)
        self._assertLocationHeader(response, redirect_url)

    def assertPermanentRedirect(self, response, request_url=None):
        self.assertStatus(response, 301)
        self._assertLocationHeader(response, redirect_url)

    def _assertLocationHeader(self, response, request_url=None):
        if request_url is None: 
            self.assertTrue(response.get("Location", None) is not None)
        else:
            self.assertEquals(response.get("Location", None), request_url)

    def assertNotAllowed(self, response, allow=None):
        self.assertEquals(response.status_code, 405)
        if allow is not None:
            self.assertEquals(response["Allow"], allow)

    def assertGone(self, response):
        self.assertEquals(response.status_code, 410)

    def assertHtml(self, response, status_code=200):
        self.assertBody(response, "<html") # open tag
        self.assertBody(response, "</html>") # close tag
        self.assertBody(response, "<head")
        self.assertBody(response, "</head>")
        self.assertBody(response, "<body")
        self.assertBody(response, "</body>")

    def assertHeader(self, response, header_name, value):
        self.assertEquals(response[header_name], value)

    def assertBody(self, response, text, count=None,
                       msg_prefix=''):
        """
        Asserts that ``text`` occurs ``count`` times in the content of the response.
        If ``count`` is None, the count doesn't matter - the assertion is true
        if the text occurs at least once in the response.
        """
        if msg_prefix:
            msg_prefix += ": "

        text = smart_str(text, response._charset)
        real_count = response.content.count(text)
        if count is not None:
            self.assertEqual(real_count, count,
                msg_prefix + "Found %d instances of '%s' in response"
                " (expected %d)" % (real_count, text, count))
        else:
            self.failUnless(real_count != 0,
                msg_prefix + "Couldn't find '%s' in response" % text)

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

    def test_static_file(self):
        response = self.client.get(reverse("repo_static_file", kwargs={"file_name":"hglogo.png"}))
        self.assertOk(response)
        self.assertHeader(response, "Content-Type", "image/png")
