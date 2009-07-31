from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Repository(models.Model):
    name = models.CharField(max_length=140)
    slug = models.SlugField(unique=True,
        help_text='Would be the name of the repo. Do not use "-" inside the name')
    owner = models.ForeignKey(User)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # TODO
    #allow_archive = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'repository'
        verbose_name_plural = 'repositories'
        ordering = ['name',]
        permissions = (("can_push", "can_pull"),)

    def __unicode__(self):
        return u'%s' % self.name

    def get_repo_url(self):
        return reverse('repo_detail', args=[self.slug])

    def get_absolute_url(self):
        return self.get_repo_url()
