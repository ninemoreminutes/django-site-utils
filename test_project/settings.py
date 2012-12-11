# Python
import os
import sys

# Django
from django.conf import global_settings

# Update this module's local settings from the global settings module.
this_module = sys.modules[__name__]
for setting in dir(global_settings):
    if setting == setting.upper():
        setattr(this_module, setting, getattr(global_settings, setting))

# Absolute path to the directory containing this Django project.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'test_project.sqlite3'),
    }
}

SITE_ID = 1

STATIC_URL = '/static/'

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'devserver.middleware.DevServerMiddleware',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

ROOT_URLCONF = 'test_project.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'debug_toolbar',
    'devserver',
    'django_extensions',
    'south',
    'site_utils',
)

INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

DEVSERVER_DEFAULT_ADDR = '127.0.0.1'
DEVSERVER_DEFAULT_PORT = '8027'
