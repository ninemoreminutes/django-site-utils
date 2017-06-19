#!/usr/bin/env python

# Python
import os
import sys

# Setuptools
from setuptools import setup

# Django-Site-Utils
from site_utils import __version__

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='django-site-utils',
    version=__version__,
    author='Nine More Minutes, Inc.',
    author_email='support@ninemoreminutes.com',
    description='Django site-wide management commands and utilities.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst'),
                          'rb').read().decode('utf-8'),
    license='BSD',
    keywords='django site management',
    url='https://github.com/ninemoreminutes/django-site-utils/',
    packages=['site_utils'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django',
        'six',
    ],
    setup_requires=[],
    tests_require=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    options={
        'egg_info': {
            'tag_build': '.dev',
        },
        'build_sphinx': {
            'source_dir': 'docs',
            'build_dir': 'docs/_build',
            'all_files': True,
            'version': __version__,
            'release': __version__,
        },
        'upload_sphinx': {
            'upload_dir': 'docs/_build/html',
        },
        'upload_docs': {
            'upload_dir': 'docs/_build/html',
        },
        'aliases': {
            'dev_build': 'egg_info sdist build_sphinx',
            'release_build': 'egg_info -b "" sdist build_sphinx',
            'test': 'pytest',
        },
    },
    **extra
)
