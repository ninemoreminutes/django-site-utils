# Python
from __future__ import unicode_literals

# Django
from django.apps import apps

__all__ = ['app_is_installed', 'auth_is_installed']


def app_is_installed(app_label):
    """
    Determine whether the given app is currently installed, either by short name
    or full dotted import name.
    """
    for app_config in apps.get_app_configs():
        if app_label in (app_config.name, app_config.label):
            return True
    return False


def auth_is_installed():
    """
    Return whether django.contrib.auth is installed.
    """
    return app_is_installed('django.contrib.auth')
