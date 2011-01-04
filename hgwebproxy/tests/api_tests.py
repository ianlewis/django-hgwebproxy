#:coding=utf-8:

import os

from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from hgwebproxy.tests.base import RepoTestCase
from hgwebproxy import settings as hgwebproxy_settings
from hgwebproxy.api import *

class ApiTest(RepoTestCase):

    def test_create_delete_repository(self):
        repo_dir = os.path.join(hgwebproxy_settings.TEST_REPO_ROOT, "test_create")
        create_repository(repo_dir)
        self.assertTrue(os.path.isdir(repo_dir))
        self.assertTrue(os.path.isdir(os.path.join(repo_dir, ".hg")))

        delete_repository(repo_dir)
        self.assertFalse(os.path.exists(os.path.join(repo_dir, ".hg")))
        self.assertFalse(os.path.exists(repo_dir))
