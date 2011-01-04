#!/bin/sh

DJANGO_VERSIONS="1.1 1.2"
HG_VERSIONS="1.3.1 1.4.3 1.5.4 1.6.3"

set -e
python bootstrap.py
./bin/buildout

set +e
for DJANGO_VER in $DJANGO_VERSIONS
do
    for HG_VER in $HG_VERSIONS
    do
        TESTSCRIPT=./bin/test-django-$DJANGO_VER-hg-$HG_VER
        echo $TESTSCRIPT
        $TESTSCRIPT
    done
done
