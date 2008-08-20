import os, re, cgi
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
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
        self.env['PATH_INFO'] = self.env['PATH_INFO'].lstrip("/hg")

        # Make sure there's a content-length.
        if not self.env.has_key('CONTENT_LENGTH'):
            self.env['CONTENT_LENGTH'] = 0

        lf = open("/tmp/django.log", 'w')
        lf.write("self.env is %s"%self.env)
        lf.close()

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

def digest_auth(request, realm, opaque, users):
    auth_string = request.META.get('HTTP_AUTHORIZATION', None)

    if auth_string is None and not str(auth_string).startswith("Digest"):
        return False

    parts = auth_string.lstrip("Digest ").split(",")

    auth = { }

    for part in parts: # `partition' only in 2.5
        segs = part.lstrip().split("=")
        auth[segs[0]] = '='.join(segs[1:]).strip('"')

    # Quick opaque check
    if not opaque == auth['opaque']:
        return False

    for ha1 in users:
        ha2 = md5("%(method)s:%(path)s" % { 'method': request.method,
                                            'path': request.get_full_path() })

        response = md5("%(ha_one)s:%(nonce)s:%(nc)s:%(cnonce)s:%(qop)s:%(ha_two)s" \
            % { 'ha_one': ha1, 'ha_two': ha2.hexdigest(), 
                'nonce': auth['nonce'], 'nc': auth['nc'],
                'cnonce': auth['cnonce'], 'qop': auth['qop'] })
                
        if response.hexdigest() == auth['response']:
            return auth['username']
    
    return False

def hgroot(request, *args):
    resp = HttpResponse()
    hgr = _hgReqWrap(request, resp)

    config = 'hgweb.conf'
    os.environ['HGRCPATH'] = config

    if request.method == "POST":
        realm = "hg@%s" % settings.SITE_NAME
        nonce = md5(str(datetime.now())+realm).hexdigest()
        opaque = md5(settings.SITE_NAME).hexdigest()

        users = settings.HG_DIGEST_USERS
        authed = digest_auth(request, realm, opaque, users)

        if not authed:
            resp.status_code = 401
            resp['WWW-Authenticate'] = '''Digest realm="%s", qop="auth", nonce="%s", opaque="%s"''' % (realm, nonce, opaque)
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
