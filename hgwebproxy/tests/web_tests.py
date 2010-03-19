#:coding=utf-8:

from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from hgwebproxy import settings as hgwebproxy_settings

class RequestTestCase(DjangoTestCase):

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

    def assertHtml(self, response):
        self.assertContains(response, "<html") # open tag
        self.assertContains(response, "</html>") # close tag
        self.assertContains(response, "<head")
        self.assertContains(response, "</head>")
        self.assertContains(response, "<body")
        self.assertContains(response, "</body>")

    def assertHeader(self, response, header_name, value):
        self.assertEquals(response[header_name], value)

class HgWebTest(RequestTestCase):
    fixtures = ['basic.json']

    def test_hgwebdir_top(self):
        response = self.client.get(reverse("repo_list"))
        self.assertOk(response)
        self.assertHtml(response)

class HGWebDirPublicTest(RequestTestCase):
    fixtures = ['basic.json']

    def setUp(self):
        hgwebproxy_settings.REPO_LIST_REQUIRES_LOGIN = True

    def tearDown(self):
        hgwebproxy_settings.REPO_LIST_REQUIRES_LOGIN = False

    def test_public_repo_list(self):
        response = self.client.get(reverse("repo_list"))
        self.assertRedirect(response, "http://testserver%s" % settings.LOGIN_URL)

    # TODO: Initialize test repo. Make a mock mercurial repo?
    #def test_reader_repo_list(self):
    #    self.client.login(username="reader", password="reader")
    #    response = self.client.get(reverse("repo_list", kwargs={"pattern":""}))
    #    self.assertOk(response)
    #    self.assertHtml(response)
    #    self.assertContains(response, "test-repo")

class DebugStaticFilesTest(RequestTestCase):

    def setUp(self):
        self.old_debug = settings.DEBUG
        settings.DEBUG = True

    def tearDown(self):
        settings.DEBUG = self.old_debug

    def test_static_file(self):
        response = self.client.get(reverse("repo_static_file", kwargs={"file_name":"hglogo.png"}))
        self.assertOk(response)
        self.assertHeader(response, "Content-Type", "image/png")
