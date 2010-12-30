__docformat__ = "restructedtext"

import os
import re

from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_str 
from django.contrib.auth.models import User
from django.contrib.admin.util import unquote
from django.contrib import admin
from django import forms

from hgwebproxy.proxy import HgRequestWrapper
from hgwebproxy.models import Repository
from hgwebproxy.settings import *

from mercurial.hgweb import hgwebdir, hgweb
from mercurial import hg, ui

class RepositoryAdminForm(forms.ModelForm):
    class Meta:
        model = Repository

    def clean_location(self):
        """
        Checks the repository location to make sure it exists and
        is writable. 
        """
        location = self.cleaned_data["location"]

        if re.match("[\w\d]+://", location):
            raise forms.ValidationError(_("Remote repository locations are not supported"))

        if not os.path.exists(os.path.join(location, '.hg')):
            if not os.path.exists(location):
                parent_dir = os.path.normpath(os.path.join(location, ".."))
                if not os.path.exists(parent_dir):
                    raise forms.ValidationError(_("This path does not exist."))
                perm_check_path = parent_dir
            else:
                perm_check_path = location

            if not os.access(perm_check_path, os.W_OK):
                raise forms.ValidationError(_("You don't have sufficient permissions to create a repository at this path."))

        return self.cleaned_data["location"]
    
    def clean_style(self):
        """
        Checks the style to see if a path is returned by
        mercurial's templater. If no path is returned
        then the style is assumed to be invalid or not installed.
        """
        from mercurial.templater import templatepath
        if not templatepath(self.cleaned_data["style"]):
            raise forms.ValidationError(_("'%s' is not an available style." % self.cleaned_data["style"]))
        return self.cleaned_data["style"]

    def clean(self):
        """
        Performs repository creation. This is done here
        so that if any errors occur we can return to the
        admin form.
        """
        cleaned_data = self.cleaned_data
        location = self.cleaned_data.get("location")

        # If we are creating the repository and it
        # doesn't already exist on disk then create it.
        if location and not os.path.exists(os.path.join(location, '.hg')):
            try:
                if not os.path.exists(location):
                    os.mkdir(location)

                from mercurial import commands,ui
                commands.init(ui.ui(), location)
            except (IOError, OSError), e:
                raise forms.ValidationError(_("An error occurred creating the repository."))

        return cleaned_data

class RepositoryAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['name', 'owner']
    prepopulated_fields = {
        'slug': ('name',)
    }
    filter_horizontal = (
        'readers','reader_groups',
        'writers','writer_groups',
        'admins', 'admin_groups',
    )
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'owner', 'location', 'description')
        }),
        ('Permissions', {
            'fields': (
                'readers', 'writers', 'admins',
                'reader_groups', 'writer_groups', 'admin_groups',
            ),
            'classes': ('collapse',)
        }),
        ('Options', {
            'fields': ('style', 'allow_archive',),
            'classes': ('collapse',)
        }),
    )
    form = RepositoryAdminForm

    def explore(self, request, id, *args):
        opts = self.model._meta
        app_label = opts.app_label

        response = HttpResponse()
        repo = get_object_or_404(Repository, pk=id)
        hgr = HgRequestWrapper(
            request,
            response,
            script_name=repo.get_admin_explore_url(),
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

        hgserve.repo.ui.setconfig('web', 'description', smart_str(repo.description))
        hgserve.repo.ui.setconfig('web', 'name', smart_str(hgserve.reponame))
        # encode('utf-8') FIX "decoding Unicode is not supported" exception on mercurial
        hgserve.repo.ui.setconfig('web', 'contact', smart_str(repo.owner.get_full_name()))
        hgserve.repo.ui.setconfig('web', 'allow_archive', repo.allow_archive)
        hgserve.repo.ui.setconfig('web', 'style', 'monoblue_plain')
        hgserve.repo.ui.setconfig('web', 'baseurl', repo.get_admin_explore_url())
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "owner":
                queryset = kwargs.get('queryset', User.objects.all())
                kwargs["queryset"] = queryset.filter(pk=request.user.pk)
        return super(RepositoryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def change_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        if (obj.has_view_permission(request.user) and not
                obj.has_change_permission(request.user)):
            return redirect(obj)
        else:
            return super(RepositoryAdmin, self).change_view(request, object_id, extra_context)

    def queryset(self, request):
        return Repository.objects.has_view_permission(request.user)
    
    def has_change_permission(self, request, obj=None):
        has_perm = super(RepositoryAdmin, self).has_change_permission(request, obj)
        if obj:
            has_perm = has_perm and obj.has_change_permission(request.user)
        return has_perm

    def has_delete_permission(self, request, obj=None):
        has_perm = super(RepositoryAdmin, self).has_delete_permission(request, obj)
        if obj:
            has_perm = has_perm and obj.has_delete_permission(request.user)
        return has_perm

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
