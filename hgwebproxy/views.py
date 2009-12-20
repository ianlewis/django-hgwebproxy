from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404

from django.contrib.auth.models import User

from authority.decorators import permission_required_or_403

from hgwebproxy.proxy import HgRequestWrapper
from hgwebproxy.utils import is_mercurial, basic_auth
from hgwebproxy.models import Repository
from hgwebproxy.permissions import RepositoryPermission
from hgwebproxy.settings import *

from mercurial.hgweb import hgwebdir, hgweb, common, webutil
from mercurial import ui, hg, util, templater
from mercurial import error, encoding

"""
Simple Django view code that proxies requests through
to `hgweb` and handles authentication on `POST` up against
Djangos own built in authentication layer.
"""

def repo_list(request, pattern):
    # Handle repo_detail
    slug = pattern.split('/')[0]
    try:
        repo = Repository.objects.get(slug=slug)
        return repo_detail(request, slug=slug)
    except Repository.DoesNotExist:
        pass

    u = ui.ui()
    u.setconfig('ui', 'report_untrusted', 'off')
    u.setconfig('ui', 'interactive', 'off')
    response = HttpResponse()

    #TODO: Is this right?
    url = request.path
    if not url.endswith('/'):
        url += '/'

    def header(**map):
        yield tmpl('header', encoding=encoding.encoding, **map)

    def footer(**map):
        yield tmpl("footer", **map)

    def motd(**map):
        yield "" 

    def archivelist(ui, nodeid, url):
        # TODO: support archivelist
        if 1 == 2:  
            yield ""

    def entries(sortcolumn="", descending=False, subdir="", **map):
        #TODO: Support sort and parity
        #TODO: Support permissions
        perm = RepositoryPermission(request.user)
        repos = Repository.objects.all()
        for repo in repos:
            if perm.browse_repository(repo): 
                contact = repo.owner.get_full_name().encode('utf-8') 

                lastchange = (common.get_mtime(repo.location), util.makedate()[1])
                 
                row = dict(contact=contact or "unknown",
                           contact_sort=contact.upper() or "unknown",
                           name=repo.name,
                           name_sort=repo.name,
                           url=repo.get_absolute_url(),
                           description=repo.description or "unknown",
                           description_sort=repo.description.upper() or "unknown",
                           lastchange=lastchange,
                           lastchange_sort=lastchange[1]-lastchange[0],
                           archives=archivelist(u, "tip", url))
                yield row

    if settings.DEBUG:
        # Handle static files 
        if pattern.startswith("static/"): 
            static = templater.templatepath('static')
            fname = pattern[7:]
            req = HgRequestWrapper(
                request,
                response,
                script_name=url,
            )
            response.write(''.join([each for each in (common.staticfile(static, fname, req))]))
            return response

    defaultstaticurl = url + 'static/'
    staticurl = STATIC_URL or defaultstaticurl if not settings.DEBUG else defaultstaticurl 

    if TEMPLATE_PATHS is not None:
        hgserve.templatepath = TEMPLATE_PATHS 

    #TODO: clean this up
    vars = {}
    #TODO: Support setting the style
    style = "coal"
    #style = self.style
    #if 'style' in req.form:
    #    vars['style'] = style = req.form['style'][0]
    start = url[-1] == '?' and '&' or '?'

    sessionvars = webutil.sessionvars(vars, start)
    
    mapfile = templater.stylemap(style)
    tmpl = templater.templater(mapfile,
                               defaults={"header": header,
                                         "footer": footer,
                                         "motd": motd,
                                         "url": url,
                                         "staticurl": staticurl,
                                         "sessionvars": sessionvars})

    #TODO: Add support for descending, sortcolumn etc.
    sortdefault = 'name', False
    sortcolumn, descending = sortdefault
    sortable = ["name", "description", "contact", "lastchange"]
    sort = [("sort_%s" % column,
             "%s%s" % ((not descending and column == sortcolumn)
                        and "-" or "", column))
            for column in sortable]

    chunks = tmpl("index", entries=entries, subdir="",
                    sortcolumn=sortcolumn, descending=descending,
                    **dict(sort))
    
    for chunk in chunks:
        response.write(chunk)
    return response

@permission_required_or_403('repository_permission.browse_repository',
    (Repository, 'slug__iexact', 'slug'))
def repo_detail(request, slug):
    repo = get_object_or_404(Repository, slug=slug)
    response = HttpResponse()
    hgr = HgRequestWrapper(
        request,
        response,
        script_name=repo.get_absolute_url(),
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

    if TEMPLATE_PATHS is not None:
        hgserve.templatepath = TEMPLATE_PATHS 

    hgserve.repo.ui.setconfig('web', 'description', repo.description)
    hgserve.repo.ui.setconfig('web', 'name', hgserve.reponame)
    # encode('utf-8') FIX "decoding Unicode is not supported" exception on mercurial
    hgserve.repo.ui.setconfig('web', 'contact', repo.owner.get_full_name().encode('utf-8') )
    hgserve.repo.ui.setconfig('web', 'allow_archive', repo.allow_archive)
    # TODO: Support setting the style
    hgserve.repo.ui.setconfig('web', 'style', 'coal')
    hgserve.repo.ui.setconfig('web', 'baseurl', repo.get_absolute_url() )

    #Allow serving static content from a seperate URL
    if not settings.DEBUG:
        hgserve.repo.ui.setconfig('web', 'staticurl', STATIC_URL)

    # Allow hgweb errors to propagate
    response.write(''.join([each for each in hgserve.run_wsgi(hgr)]))
    return response
