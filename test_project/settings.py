# Python
from __future__ import unicode_literals
import os


# Absolute path to the directory containing this Django project.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

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
                'site_utils.context_processors.hostname',
                'site_utils.context_processors.settings',
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
    # 'fortunecookie',
    'polymorphic',
    # 'sortedm2m',
    # 'storages',
    'site_utils',
    'test_project.test_app',
)

INTERNAL_IPS = ('127.0.0.1',)

RUNSERVER_DEFAULT_ADDR = '127.0.0.1'
RUNSERVER_DEFAULT_PORT = '8027'


SITE_ERROR_TEMPLATES = [
    (r'^admin-site/', 'admin/error.html'),
    (r'^', 'site_utils/error.html'),
]
