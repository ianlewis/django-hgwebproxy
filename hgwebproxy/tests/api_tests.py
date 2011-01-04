#:coding=utf-8:

import os

from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from hgwebproxy.api import *
from hgwebproxy.models import Repository

BASE_DIR = getattr(settings, 'HGWEBPROXY_BASE_DIR', settings.MEDIA_ROOT)

class ApiTest(DjangoTestCase):
    fixtures = ['basic.json']

    def setUp(self):
        if not os.path.exists(BASE_DIR):
            os.makedirs(BASE_DIR)

        # Delete all repositories in the base directory
        import shutil
        for path in os.listdir(BASE_DIR):
            shutil.rmtree(os.path.join(BASE_DIR, path))

    def tearDown(self):
        # Leave items in the base directory in case of
        # test failures. Developers can check these repositories
        # to get clues as to what went wrong.
        pass

    def test_create_delete_repository(self):
        repo_dir = os.path.join(BASE_DIR, "test_create")
        create_repository(repo_dir)
        self.assertTrue(os.path.isdir(repo_dir))
        self.assertTrue(os.path.isdir(os.path.join(repo_dir, ".hg")))

        delete_repository(repo_dir)
        self.assertFalse(os.path.exists(os.path.join(repo_dir, ".hg")))
        self.assertFalse(os.path.exists(repo_dir))
