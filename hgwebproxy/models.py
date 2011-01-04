from django.db import models
from django.db.models import permalink, Q
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _

from api import *

class RepositoryManager(models.Manager):
    def has_view_permission(self, user):
        if not self._has_model_perm(user, 'view'):
            return self.none()
        else:
            return self._readable(user)

    def has_pull_permission(self, user):
        if not self._has_model_perm(user, 'pull'):
            return self.none()
        else:
            return self._readable(user)

    def has_push_permission(self, user):
        if not self._has_model_perm(user, 'push'):
            return self.none()
        else:
            return self._writable(user)

    def has_change_permission(self, user):
        if not self._has_model_perm(user, 'change'):
            return self.none()
        else:
            return self._admin(user)

    def has_delete_permission(self, user):
        if not self._has_model_perm(user, 'delete'):
            return self.none()
        else:
            return self._admin(user)

    def _has_model_perm(self, user, perm):
        opts = Repository._meta
        # Special case for custom permissions.
        if perm in ('view', 'push', 'pull'):
            perm_name = '%s_repository' % perm
        else:
            perm_name = getattr(opts, 'get_%s_permission' % perm, lambda: False)()
        return user.has_perm(opts.app_label + '.' + perm_name)

    def _readable(self, user):
        if user.is_superuser:
            return self.all()
        return self.filter(
            Q(owner = user) | 
            Q(readers = user) |
            Q(writers = user) |
            Q(admins = user) |
            Q(reader_groups__in=user.groups.all()) |
            Q(writer_groups__in=user.groups.all()) |
            Q(admin_groups__in=user.groups.all())
        )

    def _writable(self, user): 
        if user.is_superuser:
            return self.all()
        return self.filter(
            Q(owner = user) | 
            Q(writers = user) |
            Q(admins = user) |
            Q(writer_groups__in=user.groups.all()) |
            Q(admin_groups__in=user.groups.all())
        )

    def _admin(self, user):
        if user.is_superuser:
            return self.all()
        return self.filter(
            Q(owner = user) | 
            Q(admins = user) |
            Q(admin_groups__in=user.groups.all())
        )

def _qs_exists(qs):
    return not not qs.values("pk")[:1]

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
                             help_text=_('The hgweb style'))

    readers = models.ManyToManyField(User, related_name="repository_readable_set", blank=True, null=True)
    writers = models.ManyToManyField(User, related_name="repository_writeable_set", blank=True, null=True)
    admins = models.ManyToManyField(User, related_name="repository_admin_set", blank=True, null=True)
    reader_groups = models.ManyToManyField(Group, related_name="repository_readable_set", blank=True, null=True)
    writer_groups = models.ManyToManyField(Group, related_name="repository_writeable_set", blank=True, null=True)
    admin_groups = models.ManyToManyField(Group, related_name="repository_admin_set", blank=True, null=True)

    objects = RepositoryManager()

    def __unicode__(self):
        return u'%s' % self.name

    def _is_reader(self, user):
        return (
            _qs_exists(self.readers.filter(pk=user.pk)) or
            _qs_exists(self.reader_groups.filter(
                pk__in=map(lambda g: g.pk, user.groups.all())))
        )

    def _is_writer(self, user):
        return (
            _qs_exists(self.writers.filter(pk=user.pk)) or
            _qs_exists(self.writer_groups.filter(
                pk__in=map(lambda g: g.pk, user.groups.all())))
        )

    def _is_admin(self, user):
        return (
            user.is_superuser or
            user.pk == self.owner_id or
            _qs_exists(self.admins.filter(pk=user.pk)) or
            _qs_exists(self.admin_groups.filter(
                pk__in=map(lambda g: g.pk, user.groups.all())))
        )
    has_change_permission = _is_admin
    has_delete_permission = _is_admin

    def has_view_permission(self, user):
        return (
            self._is_reader(user) or
            self._is_writer(user) or
            self._is_admin(user)
        )
    can_browse = has_view_permission
    has_pull_permission = has_view_permission
    can_pull = has_pull_permission
    
    def has_push_permission(self, user):
        return (
            self._is_writer(user) or
            self._is_admin(user)
        )
    can_push = has_push_permission

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
        permissions = (
            ("view_repository", "Can view repository"),
            ("push_repository", "Can push to repository"),
            ("pull_repository", "Can pull from repository"),
        )
