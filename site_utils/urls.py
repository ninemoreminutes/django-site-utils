# Django
from django.conf.urls import url
from django.utils.module_loading import import_string

__all__ = ['handler400', 'handler403', 'handler404', 'handler500']


handler400 = 'site_utils.views.handle_400'
handler403 = 'site_utils.views.handle_403'
handler404 = 'site_utils.views.handle_404'
handler500 = 'site_utils.views.handle_500'

urlpatterns = [
    # FIXME: Make admin prefix configurable.
    url(r'^(?:admin/)?400.html$', import_string(handler400), name='bad-request'),
    url(r'^(?:admin/)?403.html$', import_string(handler403), name='forbidden'),
    url(r'^(?:admin/)?404.html$', import_string(handler404), name='not-found'),
    url(r'^(?:admin/)?500.html$', import_string(handler500), name='server-error'),
]
