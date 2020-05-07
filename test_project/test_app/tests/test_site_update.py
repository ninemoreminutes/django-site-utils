# Python
from __future__ import unicode_literals

# Django
from django.core.management import get_commands, load_command_class, BaseCommand, CommandError

# Test App
from . import trackcalls


def get_command_class(name):
    app_name = get_commands()[name]
    if isinstance(app_name, BaseCommand):
        instance = app_name
    else:
        instance = load_command_class(app_name, name)
    return type(instance)


def track_command_class(name):
    klass = get_command_class(name)
    klass.execute = trackcalls(klass.execute)
    assert not klass.execute.has_been_called


def get_command_called(name):
    klass = get_command_class(name)
    return getattr(klass.execute, 'has_been_called', None)


def test_site_update_default(command_runner, settings):
    # Run site update with built-in default options, verify only expected
    # commands have been called.
    track_command_class('check')
    track_command_class('migrate')
    track_command_class('collectstatic')
    track_command_class('flush')
    result = command_runner('site_update', interactive=False)
    assert result[0] is None
    assert get_command_called('check')
    assert get_command_called('migrate')
    assert get_command_called('collectstatic')
    assert not get_command_called('flush')


def test_site_update_list_groups(command_runner, settings):
    result = command_runner('site_update', list_groups=True, verbosity=1)
    assert result[0] is None
    assert '[default]' in result[1]
    assert 'migrate(' not in result[1]
    result = command_runner('site_update', list_groups=True, verbosity=2)
    assert result[0] is None
    assert '[default]' in result[1]
    assert 'migrate(' in result[1]


def test_site_update_custom_default_group(command_runner, settings):
    # Replace the default update commands via settings, then verify that the
    # updated list of 'default' commands was used.
    settings.SITE_UPDATE_COMMANDS = {
        'default': [
            'check',
            'migrate',
            ('update_permissions', (), {}, 'django_extensions'),
            ('collectstatic', (), {'clear': True}, 'staticfiles'),
        ],
    }
    track_command_class('check')
    track_command_class('migrate')
    track_command_class('update_permissions')
    track_command_class('collectstatic')
    track_command_class('flush')
    result = command_runner('site_update', interactive=False)
    assert result[0] is None
    assert get_command_called('check')
    assert get_command_called('migrate')
    assert get_command_called('update_permissions')
    assert get_command_called('collectstatic')
    assert not get_command_called('flush')


def test_site_update_new_group(command_runner, settings):
    # Create a new group of update commands via settings, run site_update with
    # 'clean' subcommand and verify only the expected commands were called.
    settings.SITE_UPDATE_COMMANDS = {
        'clean': [
            ('remove_stale_contenttypes', (), {}, 'contenttypes'),
            ('clearsessions', (), {}, 'sessions'),
        ],
    }
    track_command_class('check')
    track_command_class('migrate')
    track_command_class('collectstatic')
    track_command_class('remove_stale_contenttypes')
    track_command_class('clearsessions')
    result = command_runner('site_update', 'clean', interactive=False)
    assert result[0] is None
    assert not get_command_called('check')
    assert not get_command_called('migrate')
    assert not get_command_called('collectstatic')
    assert get_command_called('remove_stale_contenttypes')
    assert get_command_called('clearsessions')


def test_site_update_multiple_groups(command_runner, settings):
    # Define a new group of subcommands, which will be merged with default
    # settings to include the default group. Run using 'default' and 'clean'
    # subcommands, verify that all commands in both groups were called.
    settings.SITE_UPDATE_COMMANDS = {
        'clean': [
            ('remove_stale_contenttypes', (), {}, 'contenttypes'),
            ('clearsessions', (), {}, 'sessions'),
        ],
    }
    track_command_class('check')
    track_command_class('migrate')
    track_command_class('collectstatic')
    track_command_class('remove_stale_contenttypes')
    track_command_class('clearsessions')
    result = command_runner('site_update', 'default', 'clean', interactive=False)
    assert result[0] is None
    assert get_command_called('check')
    assert get_command_called('migrate')
    assert get_command_called('collectstatic')
    assert get_command_called('remove_stale_contenttypes')
    assert get_command_called('clearsessions')


def test_site_update_app_not_installed(command_runner, settings):
    # Define a new group with a subcommand that only runs if the 'blah' app is
    # installed. Run using 'blah' subcommand should still succeed since
    # 'blahapp' is specified and not installed.
    settings.SITE_UPDATE_COMMANDS = {
        'blah': [
            ('blah', (), {}, 'blahapp'),
        ],
    }
    track_command_class('check')
    result = command_runner('site_update', 'blah', interactive=False)
    assert result[0] is None
    assert not get_command_called('check')


def test_site_update_unknown_command(command_runner, settings):
    # Define a new group with an invalid command, should fail since 'argh' is
    # an unknown command.
    settings.SITE_UPDATE_COMMANDS = {
        'argh': [
            'argh',
        ],
    }
    result = command_runner('site_update', 'argh', interactive=False)
    assert isinstance(result[0], CommandError)


def test_site_update_invalid_command_specs(command_runner, settings):
    # Define groups with invalid command specifications; both should fail.
    settings.SITE_UPDATE_COMMANDS = {
        'wtf': [
            (),
        ],
        'wtf2': [
            None,
        ],
    }
    result = command_runner('site_update', 'wtf', interactive=False)
    assert isinstance(result[0], CommandError)
    result = command_runner('site_update', 'wtf2', interactive=False)
    assert isinstance(result[0], CommandError)


def test_site_update_unknown_group(command_runner, settings):
    # Run with unknown subcommand (unknown group); should fail.
    result = command_runner('site_update', 'hoohah', interactive=False)
    assert isinstance(result[0], CommandError)
