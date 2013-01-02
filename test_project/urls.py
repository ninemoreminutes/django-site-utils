# Django
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('')

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
    admin.autodiscover()
    urlpatterns += patterns('django.views.generic.simple',
        url(r'^$', 'redirect_to', {'url': '/admin/'}),
    )
    urlpatterns += patterns('',
        url(r'^admin/', include(admin.site.urls)),
    )

if 'django.contrib.staticfiles' in settings.INSTALLED_APPS and settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
