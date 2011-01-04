#:coding=utf-8:

import os
import shutil

from django.contrib.auth.models import User, Group
from django.test import TestCase as DjangoTestCase
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

    def tearDown(self):
        # Leave items in the base directory in case of
        # test failures. Developers can check these repositories
        # to get clues as to what went wrong.
        pass
