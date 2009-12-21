__docformat__ = "restructedtext"

import os

from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib import admin

from hgwebproxy.proxy import HgRequestWrapper
from hgwebproxy.models import Repository
from hgwebproxy.settings import *

from mercurial.hgweb import hgwebdir, hgweb
from mercurial import hg, ui

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner']
    prepopulated_fields = {
        'slug': ('name',)
    }
    filter_horizontal = ('readers','reader_groups','writers','writer_groups')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'owner', 'location', 'description', 'allow_archive')
        }),
        ('Permissions', {
            'fields': ('readers', 'writers', 'reader_groups', 'writer_groups')
        }),
    )
    

    def explore(self, request, id, *args):
        opts = self.model._meta
        app_label = opts.app_label

        response = HttpResponse()
        repo = get_object_or_404(Repository, pk=id)
        hgr = HgRequestWrapper(
            request,
            response,
            reponame=repo.slug,
            repourl=repo.get_admin_explore_url(),
        )
        hgr.set_user(request.user.username)

        """
        Run the `hgwebdir` method from Mercurial directly, with
        our incognito request wrapper, output will be buffered. Wrapped
        in a try:except: since `hgweb` *can* crash.

        Mercurial now sends the content through as a generator.
        We need to iterate over the output in order to get all of the content
        """

        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        hgserve = hgweb(str(repo.location))

        hgserve.reponame = repo.slug
        # TODO: A more flexible way to get the default template path of mercurial
        hgserve.templatepath = (template_dir, '/usr/share/mercurial/templates')

        hgserve.repo.ui.setconfig('web', 'description', repo.description)
        hgserve.repo.ui.setconfig('web', 'name', hgserve.reponame)
        # encode('utf-8') FIX "decoding Unicode is not supported" exception on mercurial
        hgserve.repo.ui.setconfig('web', 'contact', repo.owner.get_full_name().encode('utf-8') )
        hgserve.repo.ui.setconfig('web', 'allow_archive', repo.allow_archive)
        hgserve.repo.ui.setconfig('web', 'style', 'monoblue_plain')
        hgserve.repo.ui.setconfig('web', 'baseurl', repo.get_admin_explore_url() )
        hgserve.repo.ui.setconfig('web', 'staticurl', STATIC_URL)

        try:
            response.write(''.join([each for each in hgserve.run_wsgi(hgr)]))
        except KeyError:
            response['content-type'] = 'text/html'
            response.write('hgweb crashed.')
            # if hgweb crashed you can do what you like, throw a 404 or continue on
            # hgweb tends to throw these on invalid requests..?
            pass

        context = {
            'app_label': app_label,
            'opts': opts,
            'has_change_permission': self.has_change_permission(request, repo),
            'original': repo,
            'content': response.content,
            'reponame' : hgserve.reponame,
            'static_url' : STATIC_URL,
            'slugpath': request.path.replace(repo.get_admin_explore_url(), '') or 'summary',
            'is_root': request.path == repo.get_admin_explore_url(),
        }

        """
        In cases of downloading raw files or tarballs, we don't want to
        pass the output to our template, so instead we just return it as-is.
        """
        if response.has_header('content-type'):
            if not response['content-type'].startswith("text/html"):
                return response

        """
        Otherwise, send the content on to the template, for any kind
        of custom layout you want around it.
        """
        return render_to_response("admin/hgwebproxy/repository/explore.html", context, RequestContext(request))

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url 
        urls = super(RepositoryAdmin, self).get_urls()
        my_urls = patterns('',
            url(
                r'(?P<id>\d+)/explore',
                self.admin_site.admin_view(self.explore),
                name='hgwebproxy_repository_explore',
            ),
        )
        return my_urls + urls

admin.site.register(Repository, RepositoryAdmin)
