# Python
from __future__ import unicode_literals

# Django-Site-Utils
from site_utils.utils import app_is_installed


def test_app_is_installed(settings):
    assert app_is_installed('contenttypes')
    assert app_is_installed('django.contrib.contenttypes')
    assert app_is_installed('admin')
    assert app_is_installed('django.contrib.admin')
    assert not app_is_installed('flatpages')
    assert not app_is_installed('django.contrib.flatpages')
    assert app_is_installed('site_utils')
