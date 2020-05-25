# Django
from django.conf.urls import url
from django.utils.module_loading import import_string

# Django-Site-Utils
from .handlers import handler400, handler403, handler404, handler500


urlpatterns = [
    url(r'^400.html$', import_string(handler400), name='bad-request'),
    url(r'^403.html$', import_string(handler403), name='forbidden'),
    url(r'^404.html$', import_string(handler404), name='not-found'),
    url(r'^500.html$', import_string(handler500), name='server-error'),
]
