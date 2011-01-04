#:coding=utf-8:

from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from django.core.urlresolvers import reverse

from hgwebproxy.tests.base import RepoTestCase
from hgwebproxy.models import Repository

class PermissionTest(RepoTestCase):
    fixtures = ['basic.json']

    def assertReader(self, repo, user):
        self.assertTrue(repo.can_browse(user))
        self.assertTrue(repo.can_pull(user))
        self.assertFalse(repo.can_push(user))

    def assertWriter(self, repo, user):
        self.assertTrue(repo.can_browse(user))
        self.assertTrue(repo.can_pull(user))
        self.assertTrue(repo.can_push(user))

    def test_admin(self):
        user = User.objects.get(username="admin") 
        repo = Repository.objects.get(slug='test-repo')

        self.assertWriter(repo, user)

    def test_reader(self):
        user = User.objects.get(username="reader") 
        repo = Repository.objects.get(slug='test-repo')

        self.assertReader(repo, user)

    def test_writer(self):
        user = User.objects.get(username="writer") 
        repo = Repository.objects.get(slug='test-repo')

        self.assertWriter(repo, user)

    def test_group_reader(self):
        user = User.objects.get(username="group_reader") 
        repo = Repository.objects.get(slug='test-repo')

        self.assertReader(repo, user)

    def test_writer(self):
        user = User.objects.get(username="group_writer") 
        repo = Repository.objects.get(slug='test-repo')

        self.assertWriter(repo, user)

    def test_owner(self):
        user = User.objects.get(username="owner") 
        repo = Repository.objects.get(slug='test-repo')

        self.assertWriter(repo, user)
