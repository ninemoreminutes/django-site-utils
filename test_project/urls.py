# Django
from django.conf import settings
from django.conf.urls import include, url

# Django-Site-Utils
from site_utils.urls import handler400, handler403, handler404, handler500  # noqa

# Test App
import test_project.test_app.urls

urlpatterns = []

urlpatterns += [
    url(r'^', include(test_project.test_app.urls)),
]

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
    admin.autodiscover()
    # urlpatterns += [
    #     url(r'^$', 'django.views.generic.simpleredirect_to', {'url': '/admin/'}),
    # ]
    urlpatterns += [
        url(r'^admin-site/', include(admin.site.urls)),
    ]

if 'django.contrib.staticfiles' in settings.INSTALLED_APPS and settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
