from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _

from api import *

class Repository(models.Model):
    name = models.CharField(max_length=140)
    slug = models.SlugField(unique=True,
        help_text='Would be the name of the repo. Do not use "-" inside the name')
    owner = models.ForeignKey(User)
    location = models.CharField(max_length=200,
            help_text=_('The absolute path to the repository. If the repository does not exist it will be created.'))
    description = models.TextField(blank=True, null=True)

    allow_archive = models.CharField(max_length=100, blank=True, null=True,
        help_text=_("Same as in hgrc config, as: zip, bz2, gz"))

    style = models.CharField(max_length=256, blank=True, null=True,
        default="coal", help_text=_('The hgweb style'))

    readers = models.ManyToManyField(User, related_name="repository_readable_set", blank=True, null=True)
    writers = models.ManyToManyField(User, related_name="repository_writeable_set", blank=True, null=True)
    reader_groups = models.ManyToManyField(Group, related_name="repository_readable_set", blank=True, null=True)
    writer_groups = models.ManyToManyField(Group, related_name="repository_writeable_set", blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.name

    def can_browse(self, user):
        return user.is_superuser or \
               user == self.owner or \
               not not self.readers.filter(pk=user.id) or \
               not not self.writers.filter(pk=user.id) or \
               not not self.reader_groups.filter(pk__in=[group.id for group in user.groups.all()]) or \
               not not self.writer_groups.filter(pk__in=[group.id for group in user.groups.all()])


    def can_pull(self, user):
        return user.is_superuser or \
               user == self.owner or \
               not not self.readers.filter(pk=user.id) or \
               not not self.writers.filter(pk=user.id) or \
               not not self.reader_groups.filter(pk__in=[group.id for group in user.groups.all()]) or \
               not not self.writer_groups.filter(pk__in=[group.id for group in user.groups.all()])

    def can_push(self, user):
        return user.is_superuser or \
               user == self.owner or \
               not not self.writers.filter(pk=user.id) or \
               not not self.writer_groups.filter(pk__in=[group.id for group in user.groups.all()])

    @permalink
    def get_admin_explore_url(self):
        return ('admin:hgwebproxy_repository_explore', (), {
            'id': self.id,
        })

    @permalink
    def get_absolute_url(self):
        return ('repo_detail', (), {
            'pattern': self.slug + "/",
        })

    def save(self, *args, **kwargs):
        super(Repository, self).save(*args, **kwargs)
        create_repository(self.location)

    def delete(self, *args, **kwargs):
        super(Repository, self).delete(*args, **kwargs)
        delete_repository(self.location)

    class Meta:
        verbose_name = _('repository')
        verbose_name_plural = _('repositories')
        ordering = ['name',]
