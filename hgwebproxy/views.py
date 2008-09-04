import os, re, cgi, base64
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.template import RequestContext
from django.contrib.auth.models import User
from datetime import datetime

from mercurial.hgweb.hgwebdir_mod import hgwebdir
from mercurial import hg, ui
from mercurial import __version__

try:
    from hashlib import md5 as md5
except ImportError:
    from md5 import md5

class _hgReqWrap(object):
    def __init__(self, req, resp):
        self.django_req = req
        self.env = req.META
        self.response = resp

        # Remove the prefix so HG will think it's running on its own.
        self.env['PATH_INFO'] = self.env['PATH_INFO'].replace("/hg", "", 1)

        # Make sure there's a content-length.
        if not self.env.has_key('CONTENT_LENGTH'):
            self.env['CONTENT_LENGTH'] = 0

        self.inp = self.env['wsgi.input']
        self.form = cgi.parse(self.inp, self.env, keep_blank_values=1)

        self.headers = [ ]
        self.err = self.env['wsgi.errors']

        self.out = [ ]

    def set_user(self, username):
        self.env['REMOTE_USER'] = username

    def read(self, count=-1):
        return self.inp.read(count)

    def flush(self):
        return None

    def respond(self, code, content_type=None, path=None, length=0):
        self.response.status_code = code

        self.response['content-type'] = content_type

        if path is not None and length is not None:
            self.response['content-type'] = content_type
            self.response['content-length'] = length
            self.response['content-disposition'] = 'inline; filename=%s' % path

        for directive, value in self.headers:
            self.response[directive.lower()] = value

    def header(self, headers=[('Content-Type','text/html')]):
        self.headers.extend(headers)

    def write(self, *a):
        for thing in a:
            if hasattr(thing, '__iter__'):
                for p in thing:
                    self.write(p)
            else:
                thing = str(thing)
                self.response.write(thing)

def basic_auth(request, realm):
    auth_string = request.META.get('HTTP_AUTHORIZATION')
    
    if auth_string is None or not auth_string.startswith("Basic"):
        return False
        
    _, basic_hash = auth_string.split(' ', 1)
    username, password = basic_hash.decode('base64').split(':', 1)
    
    if authenticate(username=username, password=password):
        return username
    
    return False

def hgroot(request, *args):
    resp = HttpResponse()
    hgr = _hgReqWrap(request, resp)

    config = os.path.join(settings.BASE_DIR, 'hgwebproxy', 'hgweb.conf')
    os.environ['HGRCPATH'] = config

    if request.method == "POST":
        realm = 'Django Basic Auth' # Change me, if you want.

        authed = basic_auth(request, realm)

        if not authed:
            resp.status_code = 401
            resp['WWW-Authenticate'] = '''Basic realm="%s"''' % realm
            return resp
        else:
            hgr.set_user(authed)
        
    try:
        hgwebdir(config).run_wsgi(hgr)
    except KeyError:
        resp['content-type'] = 'text/html'
        resp.write('hgweb crashed.')
        pass # hgweb tends to throw these on invalid requests..?
             # nothing to do but ignore it. hg >1.0 might fix.

    if resp.has_header('content-type'):
        if not resp['content-type'].startswith("text/html"):
            return resp

    return render_to_response("flat.html", {
        'content': resp.content, 'slugpath': request.path.lstrip("/hg"),
        'hg_version': __version__.version, 'is_root': request.path == '/hg/' },
        RequestContext(request))
