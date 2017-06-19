# Python
import os
import sys

# Django
import django
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

ADMINS = (
    ('Chris Church', 'chris@ninemoreminutes.com'),
)

MANAGERS = (
    ('David Horton', 'david@ninemoreminutes.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'test_project.sqlite3'),
    }
}

TIME_ZONE = 'America/New_York'

SECRET_KEY = 'af8f979c3ac99c59885f229e045c1574cc510afb'

SITE_ID = 1

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'public', 'static')

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'public', 'media')

if django.VERSION >= (1, 10):
    MIDDLEWARE = (locals().get('MIDDLEWARE', None) or ()) + (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
else:
    MIDDLEWARE_CLASSES = (locals().get('MIDDLEWARE_CLASSES', None) or ()) + (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

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
    'django_extensions',
    # 'storages',
    'site_utils',
    'test_project.test_app',
    'sortedm2m',
    'fortunecookie',
)

INTERNAL_IPS = ('127.0.0.1',)

RUNSERVER_DEFAULT_ADDR = '127.0.0.1'
RUNSERVER_DEFAULT_PORT = '8027'


SITE_ERROR_TEMPLATES = [
    (r'^admin-site/', 'admin/error.html'),
    (r'^', 'site_utils/error.html'),
]
