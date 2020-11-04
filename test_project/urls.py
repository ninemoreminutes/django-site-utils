# Python
from __future__ import unicode_literals

# Django
from django.conf import settings
try:
    from django.urls import include, re_path
except ImportError:
    from django.conf.urls import include, url as re_path

# Django-Site-Utils
from site_utils.handlers import handler400, handler403, handler404, handler500  # noqa
import site_utils.urls

# Test App
import test_project.test_app.urls

urlpatterns = []

urlpatterns += [
    re_path(r'^', include(test_project.test_app.urls)),
]

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
    admin.autodiscover()
    # urlpatterns += [
    #     re_path(r'^$', 'django.views.generic.simpleredirect_to', {'url': '/admin/'}),
    # ]
    urlpatterns += [
        re_path(r'^admin-site/', admin.site.urls),
    ]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'', include(site_utils.urls)),
    ]

if 'django.contrib.staticfiles' in settings.INSTALLED_APPS and settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
