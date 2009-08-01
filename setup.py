# -*- coding:utf8 -*-
from setuptools import setup, find_packages

setup(
    name='django-hgwebproxy',
    version='0.1.0',
    description='',
    long_description=open('README').read(),
    author='Mario César Señoranis Ayala',
    author_email='mariocesar.sa@openit.com.bo',
    url='http://bitbucket.org/mariocesar/django-hgweproxy/',
    install_requires=(
        'mercurial>=1.0',
        'django>=1.0',
    ),
    packages=find_packages(exclude=['example', 'docs']),
    license='GPL',
    keywords='django mercurial hg bitbucket webapp',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Natural Language :: Spanish',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe=False,
)
