from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Repository(models.Model):
    name = models.CharField(max_length=140)
    slug = models.SlugField(unique=True,
        help_text='Would be the name of the repo. Do not use "-" inside the name')
    owner = models.ForeignKey(User)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    allow_archive = models.CharField(max_length=100, blank=True, null=True,
        help_text="Same as in hgrc config, as: zip, bz2, gz")

    class Meta:
        verbose_name = _('repository')
        verbose_name_plural = _('repositories')
        ordering = ['name',]
        permissions = (
            ("can_push", "Can Push"),
            ("can_pull", "Can Pull"),
        )

    def __unicode__(self):
        return u'%s' % self.name

    @permalink
    def get_admin_explore_url(self):
        return ('admin:hgwebproxy_repository_explore', (), {
            'id': self.id,
        })

    #def get_absolute_url(self):
    #    return self.get_repo_url()
