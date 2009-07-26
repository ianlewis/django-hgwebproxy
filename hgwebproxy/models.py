from django.db import models
from django.contrib.auth.models import User

class Repository(models.Model):
    name = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)
    owner = models.ForeignKey(User)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'repository'
        verbose_name_plural = 'repositories'
        ordering = ['name',]
        permissions = (("can_push", "can_pull"),)

    def __unicode__(self):
        return u'%s' % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('hgwebproxy.views.repo', (), {'slug': self.slug})
