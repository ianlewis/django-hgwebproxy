from setuptools import setup, find_packages

setup(
    name='django-hgwebproxy',
    version='0.1.0',
    description='',
    long_description=open('README').read(),
    author='',
    author_email='',
    url='http://bitbucket.org/mariocesar/hgweproxy/',
    install_requires=(
        'mercurial>=1.0',
        'django>=1.0',
    ),
    packages=find_packages(exclude=['example', 'docs']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe=False,
)
