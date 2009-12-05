from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404

from django.contrib.auth.models import User

from hgwebproxy.proxy import HgRequestWrapper
from hgwebproxy.utils import is_mercurial, basic_auth
from hgwebproxy.models import Repository
from hgwebproxy.settings import *

from mercurial.hgweb import hgwebdir, hgweb
from mercurial import hg, ui


"""
Simple Django view code that proxies requests through
to `hgweb` and handles authentication on `POST` up against
Djangos own built in authentication layer.
"""
def repo_detail(request, slug, *args):
    response = HttpResponse()
    repo = get_object_or_404(Repository, slug=slug)
    hgr = HgRequestWrapper(
        request,
        response,
        reponame=repo.slug,
        repourl=repo.get_absolute_url(),
    )

    """
    Authenticate on all requests. To authenticate only against 'POST'
    requests, uncomment the line below the comment.

    Currently, repositories are only viewable by authenticated users.
    If authentication is only done on 'POST' request, then
    repositories are readable by anyone. but only authenticated users
    can push.
    """

    realm = AUTH_REALM # Change if you want.

    if is_mercurial(request):
        # This is a request by a mercurial user
        authed = basic_auth(request, realm, repo.slug)
    else:
        # This is a standard web request
        if not request.user.is_authenticated():
            return HttpResponseRedirect('%s?next=%s' %
                                        (settings.LOGIN_URL,request.path))
        else:
            authed = request.user.username

    if not authed:
        response.status_code = 401
        response['WWW-Authenticate'] = '''Basic realm="%s"''' % realm
        return response
    else:
        hgr.set_user(authed)

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
    # Allow users to set this in the admin?
    #hgserve.templatepath = (template_dir, '/usr/share/mercurial/templates')

    hgserve.repo.ui.setconfig('web', 'description', repo.description)
    hgserve.repo.ui.setconfig('web', 'name', hgserve.reponame)
    # encode('utf-8') FIX "decoding Unicode is not supported" exception on mercurial
    hgserve.repo.ui.setconfig('web', 'contact', repo.owner.get_full_name().encode('utf-8') )
    hgserve.repo.ui.setconfig('web', 'allow_archive', repo.allow_archive)
    hgserve.repo.ui.setconfig('web', 'style', 'coal')
    hgserve.repo.ui.setconfig('web', 'baseurl', repo.get_absolute_url() )

    #TODO: Allow serving static content from a seperate URL
    #hgserve.repo.ui.setconfig('web', 'staticurl', STATIC_URL)

    # Allow hgweb errors to propagate
    response.write(''.join([each for each in hgserve.run_wsgi(hgr)]))
    return response
