#!/usr/bin/env python

# Python
import sys

# Setuptools
from setuptools import setup, find_packages

# Django-Site-Utils
from site_utils import __version__

setup(
    name='django-site-utils',
    version=__version__,
    author='Nine More Minutes, Inc.',
    author_email='support@ninemoreminutes.com',
    description='Django site-wide management commands and utilities.',
    long_description=file('README', 'rb').read(),
    license='BSD',
    keywords='django site',
    url='https://projects.ninemoreminutes.com/projects/django-site-utils/',
    packages=find_packages(exclude=['test_project']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Django>=1.3',
    ],
    setup_requires=[],
    tests_require=[
        'argparse',
        'Django',
        'django-debug-toolbar',
        'django-devserver',
        'django-extensions',
        'django-fortunecookie',
        'django-hotrunner>=0.2.1',
        'django-setuptest>=0.1.2',
        'django-sortedm2m',
        'South',
    ],
    test_suite='test_suite.TestSuite',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
    ],
    options={
        'egg_info': {
            'tag_svn_revision': 1,
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
        'aliases': {
            # FIXME: Add 'test' to both aliases below.
            'dev_build': 'egg_info sdist build_sphinx',
            'release_build': 'egg_info -b "" -R sdist build_sphinx',
        },
    },
)
