#:coding=utf-8:

import os

from django.contrib.auth.models import User,Permission
from django.test import TestCase as DjangoTestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from hgwebproxy.tests.base import RepoTestCase, RequestTestCaseMixin
from hgwebproxy import settings as hgwebproxy_settings

class AdminTests(RequestTestCaseMixin, RepoTestCase):
    def test_explore_forbidden(self):
        self.client.login(username="no_perms", password="no_perms")
        user = User.objects.get(username="no_perms")
        user.user_permissions.add(
            Permission.objects.get_by_natural_key(
                "view_repository",
                "hgwebproxy",
                "repository",
            )
        )
        self.assertFalse(self.test_repo.has_view_permission(user))

        response = self.client.get(reverse("admin:hgwebproxy_repository_explore", kwargs={
            'id': self.test_repo.pk,    
        }))
        self.assertAdminLogin(response)
