"""
hgwebproxy.py

Simple Django view code that proxies requests through
to `hgweb` and handles authentication on `POST` up against
Djangos own built in authentication layer.

This code is largely equivalent to the code powering Bitbucket.org.
"""


