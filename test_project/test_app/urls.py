# Django
from django.conf.urls import include, url

# Test App
import test_project.test_app.views

error_urlpatterns = [
    url(r'^bad-request/$', test_project.test_app.views.bad_request, name='bad-request'),
    url(r'^forbidden/$', test_project.test_app.views.forbidden, name='forbidden'),
    url(r'^not-found/$', test_project.test_app.views.not_found, name='not-found'),
    url(r'^server-error/$', test_project.test_app.views.server_error, name='server-error'),
]

urlpatterns = [
    url(r'^', include(error_urlpatterns, 'error-views')),
    url(r'^admin-site/', include(error_urlpatterns, 'admin-error-views')),
]
