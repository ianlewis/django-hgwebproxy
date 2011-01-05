#:coding=utf-8:

import os
import shutil

from django.contrib.auth.models import User, Group
from django.test import TestCase as DjangoTestCase
from django.utils.encoding import smart_str
from django.conf import settings

from hgwebproxy import settings as hgwebproxy_settings
from hgwebproxy.models import Repository

class RepoTestCase(DjangoTestCase):
    fixtures = ['basic.json']

    def setUp(self):
        if not os.path.exists(hgwebproxy_settings.TEST_REPO_ROOT):
            os.makedirs(hgwebproxy_settings.TEST_REPO_ROOT)

        # Delete all repositories in the base directory
        for path in os.listdir(hgwebproxy_settings.TEST_REPO_ROOT):
            shutil.rmtree(os.path.join(hgwebproxy_settings.TEST_REPO_ROOT, path))

        # Create test repository
        repo = Repository(
            name="Test Repo",
            slug="test-repo",
            owner=User.objects.get(username="owner"),
            location=os.path.join(hgwebproxy_settings.TEST_REPO_ROOT, "test_repo"),
        )
        repo.save()
        repo.readers.add(User.objects.get(username="reader"))
        repo.writers.add(User.objects.get(username="writer"))
        repo.reader_groups.add(Group.objects.get(name="readers"))
        repo.writer_groups.add(Group.objects.get(name="writers"))
        self.test_repo = repo

    def tearDown(self):
        # Leave items in the base directory in case of
        # test failures. Developers can check these repositories
        # to get clues as to what went wrong.
        pass

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

    def assertAdminLogin(self, response):
        self.assertContains(response, '<input type="submit" value="Log in" />')
