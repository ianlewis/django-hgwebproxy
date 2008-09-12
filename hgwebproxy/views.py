"""
hgwebproxy.py

Simple Django view code that proxies requests through
to `hgweb` and handles authentication on `POST` up against
Djangos own built in authentication layer.

This code is largely equivalent to the code powering Bitbucket.org.
"""

__docformat__ = "restructedtext"

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

try:
    from hashlib import md5 as md5
except ImportError:
    from md5 import md5

class _hgReqWrap(object):
    """
    Request wrapper. The main purpose of this class
    is to wrap Djangos own `HttpResponse` object, so it
    behaves largely as a `WSGI` compliant request object,
    which is what `hgweb` expects.
    
    `hgweb` does lot of `.write()` operations on the request
    object given, and we simply stream them into Django.
    
    Notice the `set_user` method, which sets the environment
    variable `REMOTE_USER` to the user you just authenticated.
    This allows `hgweb` to pick up the username as well.
    
    Example::
        >>> resp = HttpResponse()
        >>> hgr = _hgReqWrap(request, resp)
        >>> hgwebdir('path to config file').run_wsgi(hgr)
        >>> print resp.content
        ...
    """
    def __init__(self, req, resp):
        """
        Expects two parameters;
        
        Parameters::
         - `req`: The `request` object your view receives.
         - `resp`: An instance of `HttpResponse`.
        """
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
        """
        Sets the username for the request.
        `hgweb` picks up on this, call after you've authenticated.
        """
        self.env['REMOTE_USER'] = username

    def read(self, count=-1):
        return self.inp.read(count)

    def flush(self):
        """
        Doesn't do anything, but `WSGI` requires it.
        """
        return None

    def respond(self, code, content_type=None, path=None, length=0):
        """
        `hgweb` uses this for headers, and is necessary to have things
        like "Download tarball" working.
        """
        self.response.status_code = code

        self.response['content-type'] = content_type

        if path is not None and length is not None:
            self.response['content-type'] = content_type
            self.response['content-length'] = length
            self.response['content-disposition'] = 'inline; filename=%s' % path

        for directive, value in self.headers:
            self.response[directive.lower()] = value

    def header(self, headers=[('Content-Type','text/html')]):
        """
        Set a header for the request. `hgweb` uses this too.
        """
        self.headers.extend(headers)

    def write(self, *a):
        """
        Write content to a buffered stream. Can be a string
        or an iterator of strings.
        """
        for thing in a:
            if hasattr(thing, '__iter__'):
                for p in thing:
                    self.write(p)
            else:
                thing = str(thing)
                self.response.write(thing)

def basic_auth(request, realm):
    """
    Very simple Basic authentication handler which hooks
    up to Djangos underlying database of users directly.
    
    Returns the username on successful auth, can be used
    together with `set_user` on the request wrapper.
    """
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

    """
    You want to specify the path to your config file here. Look
    at `hgweb.conf` for a working example.
    """
    config = os.path.join(settings.BASE_DIR, 'hgwebproxy', 'hgweb.conf')
    os.environ['HGRCPATH'] = config
    
    """
    Authenticate on all requests. To authenticate only against 'POST'
    requests, uncomment the line below the comment.

    Currently, repositories are only viewable by authenticated users.
    If authentication is only done on 'POST' request, then
    repositories are readable by anyone. but only authenticated users
    can push.
    """
    #if request.method == "POST":
    realm = 'Django Basic Auth' # Change me, if you want.

    authed = basic_auth(request, realm)

    if not authed:
        resp.status_code = 401
        resp['WWW-Authenticate'] = '''Basic realm="%s"''' % realm
        return resp
    else:
        hgr.set_user(authed)
        
    """
    Run the `hgwebdir` method from Mercurial directly, with
    our incognito request wrapper, output will be buffered. Wrapped
    in a try:except: since `hgweb` *can* crash.
    """
    try:
        hgwebdir(config).run_wsgi(hgr)
    except KeyError:
        resp['content-type'] = 'text/html'
        resp.write('hgweb crashed.')
        pass # hgweb tends to throw these on invalid requests..?
             # nothing to do but ignore it. hg >1.0 might fix.

    """
    In cases of downloading raw files or tarballs, we don't want to
    pass the output to our template, so instead we just return it as-is.
    """
    if resp.has_header('content-type'):
        if not resp['content-type'].startswith("text/html"):
            return resp

    """
    Otherwise, send the content on to the template, for any kind
    of custom layout you want around it.
    """
    return render_to_response("flat.html", 
        { 'content': resp.content, },
        RequestContext(request))
