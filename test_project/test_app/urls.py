# Python
from __future__ import unicode_literals

# Django
from django.conf.urls import include, url

# Test App
from . import views

error_urlpatterns = [
    url(r'^bad-request/$', views.bad_request, name='bad-request'),
    url(r'^forbidden/$', views.forbidden, name='forbidden'),
    url(r'^not-found/$', views.not_found, name='not-found'),
    url(r'^server-error/$', views.server_error, name='server-error'),
]

urlpatterns = [
    url(r'^', include((error_urlpatterns, 'error-views'))),
    url(r'^admin-site/', include((error_urlpatterns, 'admin-error-views'))),
]
