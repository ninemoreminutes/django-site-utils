# Python
from __future__ import unicode_literals


def test_site_config_display_current(current_site, command_runner, settings):
    # With no options and verbosity=1, should display the current site.
    result = command_runner('site_config', verbosity=1)
    assert result[0] is None
    assert 'Name="{}"'.format(current_site.name) in result[1]
    assert 'Domain="{}"'.format(current_site.domain) in result[1]
    current_site.refresh_from_db()
    assert current_site.name == 'example.com'
    assert current_site.domain == 'example.com'


def test_site_config_display_by_id(current_site, command_runner, settings):
    # With no options and verbosity=1, should display the current site.
    result = command_runner('site_config', site_id=current_site.id, verbosity=1)
    assert result[0] is None
    assert 'Name="{}"'.format(current_site.name) in result[1]
    assert 'Domain="{}"'.format(current_site.domain) in result[1]


def test_site_config_id_not_found(command_runner, settings):
    result = command_runner('site_config', site_id=99)
    assert isinstance(result[0], Exception)


def test_site_config_change_name(current_site, command_runner, settings):
    # Change only the name.
    result = command_runner('site_config', name='example net site')
    assert result[0] is None
    current_site.refresh_from_db()
    assert current_site.name == 'example net site'
    assert current_site.domain == 'example.com'


def test_site_config_change_domain(current_site, command_runner, settings):
    # Change only the domain.
    result = command_runner('site_config', domain='example.net')
    assert result[0] is None
    current_site.refresh_from_db()
    assert current_site.name == 'example.com'
    assert current_site.domain == 'example.net'


def test_site_config_change_name_and_domain(current_site, command_runner, settings):
    # Change both name and domain.
    result = command_runner('site_config', name='example org site', domain='example.org')
    assert result[0] is None
    current_site.refresh_from_db()
    assert current_site.name == 'example org site'
    assert current_site.domain == 'example.org'


def test_site_config_without_sites_app(command_runner, settings):
    # Remove django.contrib.sites and try to run the command.
    settings.INSTALLED_APPS = (x for x in settings.INSTALLED_APPS if x != 'django.contrib.sites')
    result = command_runner('site_config')
    assert isinstance(result[0], Exception)
