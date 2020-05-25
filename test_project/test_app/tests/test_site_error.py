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


@pytest.mark.parametrize('status_code', [400, 403, 404, 500, 502, 503, 504])
def test_site_error_page_command(command_runner, settings, tmp_path, status_code):
    result = command_runner('site_error_page', status_code, dest=str(tmp_path))
    assert result[0] is None
    error_page_path = tmp_path / '{}.html'.format(status_code)
    assert error_page_path.exists()


def test_site_error_page_command_options(command_runner, settings, tmp_path):
    status_codes = [400, 403, 404, 500, 502, 503, 504]
    result = command_runner('site_error_page', *status_codes, dest=str(tmp_path), prefix='error', suffix='.htm')
    assert result[0] is None
    for status_code in status_codes:
        error_page_path = tmp_path / 'error{}.htm'.format(status_code)
        assert error_page_path.exists()
