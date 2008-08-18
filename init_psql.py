"""
Script to create POSTGRES Django database

Assumptions:
1. psql has been installed

2. TCP/IP connections are allowed. For Postgres 7.4 (default in Debian
Etch), it will be necessary to set 

tcpip_socket = true

The default is false.
"""

import os
import sys
import re

def project_dir():
    """Return application directory."""
    import os, os.path
    return os.path.dirname(os.path.abspath(__file__)).split('/')[-1]

import os
from django.core.management import setup_environ
sys.path = ['/var/django/'] + sys.path
exec("from " + project_dir() + " import settings")
setup_environ(settings)

def init_db(database):
    usr = os.popen('whoami').read().strip()
    # verbose controls whether the SQL statements are printed
    verbose = 0
    try:
        import psycopg2
    except ImportError:
        try:
            import psycopg as psycopg2
        except ImportError:
            print "Please install the python module psycopg or psycopg2"
            sys.exit()
    try:
        db = psycopg2.connect("port=5432 dbname=template1 user=%s" % usr)
    except Exception, e:
        print "Enter sudo password at prompt ..."
        os.system('sudo su postgres -c "createuser -a -d -q %s"' % usr)
        db = psycopg2.connect("port=5432 dbname=template1 user=%s" % usr)
    c = db.cursor()    
    try:
        c.execute("create user django with createdb createuser password 'pqxxrocks'")
        print "creating user django."
    except Exception, e:
        print e
    c.execute("commit")
    c.close()
    db.commit()
    db.close()
    db = psycopg2.connect("host=localhost port=5432 dbname=template1 user=django password=pqxxrocks")
    c = db.cursor()
    # create database.
    c.execute("commit") # create database cannot be within a transaction
    try:
        c.execute("create database " + database)
    except Exception, e:
        em = e.args[0]
        if "database" in em and  "already exists" in em:
            yn = raw_input(database + " database exists - delete and recreate? (Answer y or n) ")
            if yn.lower().startswith('y'):
                c.execute("commit")
                c.execute("drop database " + database)
                c.execute("commit")
                c.execute("create database " + database)
            else:
                print database +" exists - exiting ..."
                sys.exit(1)
        else:
            raise e
    try:
        os.system("python manage.py syncdb")
    except Exception, e:
        print "Ignoring:", e

init_db("hg")
