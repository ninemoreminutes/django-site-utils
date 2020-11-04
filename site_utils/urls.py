# Django
try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path
from django.utils.module_loading import import_string

# Django-Site-Utils
from .handlers import handler400, handler403, handler404, handler500


urlpatterns = [
    re_path(r'^400.html$', import_string(handler400), name='bad-request'),
    re_path(r'^403.html$', import_string(handler403), name='forbidden'),
    re_path(r'^404.html$', import_string(handler404), name='not-found'),
    re_path(r'^500.html$', import_string(handler500), name='server-error'),
]
