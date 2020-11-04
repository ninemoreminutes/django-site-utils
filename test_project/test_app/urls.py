# Python
from __future__ import unicode_literals

# Django
try:
    from django.urls import include, re_path
except ImportError:
    from django.conf.urls import include, url as re_path

# Test App
from . import views

error_urlpatterns = [
    re_path(r'^bad-request/$', views.bad_request, name='bad-request'),
    re_path(r'^forbidden/$', views.forbidden, name='forbidden'),
    re_path(r'^not-found/$', views.not_found, name='not-found'),
    re_path(r'^server-error/$', views.server_error, name='server-error'),
]

urlpatterns = [
    re_path(r'^', include((error_urlpatterns, 'error-views'))),
    re_path(r'^admin-site/', include((error_urlpatterns, 'admin-error-views'))),
]
