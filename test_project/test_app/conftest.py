# Python
from __future__ import unicode_literals
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys

# Py.Test
import pytest


@pytest.fixture
def apps(request, db):
    from django.apps import apps
    return apps


@pytest.fixture
def content_type_model(apps):
    return apps.get_model('contenttypes', 'ContentType')


@pytest.fixture
def site_model(apps):
    return apps.get_model('sites', 'Site')


@pytest.fixture
def current_site(site_model):
    site = site_model.objects.get_current()
    assert site.name == 'example.com'
    assert site.domain == 'example.com'
    return site


@pytest.fixture
def user_model(django_user_model):
    return django_user_model


@pytest.fixture
def super_user(user_model):
    user = user_model.objects.create_superuser('superfred', 'superfred@ixmm.net', 'fredsPASS')
    user.first_name = 'Super'
    user.last_name = 'Fred'
    user.save()
    return user


@pytest.fixture
def inactive_super_user(user_model):
    user = user_model.objects.create_superuser('deadfred', 'deadfred@ixmm.net', 'fredsPASS')
    user.first_name = 'Dead'
    user.last_name = 'Fred'
    user.is_active = False
    user.save()
    return user


@pytest.fixture
def staff_user(user_model):
    user = user_model.objects.create_user('stafffred', 'stafffred@ixmm.net', 'fredsPASS')
    user.first_name = 'Staff'
    user.last_name = 'Fred'
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def manager_staff_user(user_model, settings):
    settings.MANAGERS = [('Manager Fred', 'mgrfred@ixmm.net')]
    user = user_model.objects.create_user('mgrfred', 'mgrfred@ixmm.net', 'fredsPASS')
    user.first_name = 'Manager'
    user.last_name = 'Fred'
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def db_connection(db):
    from django.db import connection
    return connection


@pytest.fixture
def command_runner(db):
    from django.core.management import call_command

    def f(*args, **options):
        options.setdefault('verbosity', 0)
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        result = None
        try:
            result = call_command(*args, **options)
        except Exception as e:
            result = e
        except SystemExit as e:
            result = e
        finally:
            captured_stdout = sys.stdout.getvalue()
            captured_stderr = sys.stderr.getvalue()
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        return result, captured_stdout, captured_stderr
    return f
