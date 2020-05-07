# Python
from __future__ import unicode_literals

# Py.Test
import pytest

# Django
from django.urls import reverse


@pytest.mark.parametrize('status_code,view_name', [
    (400, 'bad-request'),
    (403, 'forbidden'),
    (404, 'not-found'),
    # (500, 'server-error'),
])
def test_error_views(client, status_code, view_name, settings):
    # Test normal error views for main site.
    url = reverse('error-views:{}'.format(view_name))
    response = client.get(url)
    assert response.status_code == status_code
    template_names = [t.name for t in response.templates if t.name is not None]
    assert 'site_utils/error.html' in template_names, response.content

    # Test alternate error views for admin site.
    url = reverse('admin-error-views:{}'.format(view_name))
    response = client.get(url)
    assert response.status_code == status_code
    template_names = [t.name for t in response.templates if t.name is not None]
    assert 'admin/error.html' in template_names


@pytest.mark.xfail()
def test_site_error_command(command_runner, settings):
    raise NotImplementedError
