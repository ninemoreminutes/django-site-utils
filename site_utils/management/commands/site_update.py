# Python
from __future__ import unicode_literals
import os

# Six
import six

# Django
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import get_commands, load_command_class, call_command, CommandError

# Django-Site-Utils
from ...utils import app_is_installed
from ...settings import get_site_utils_setting


class Command(BaseCommand):

    help = 'Execute multiple management commands.'
    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput',
            '--no-input',
            action='store_false',
            dest='interactive',
            default=True,
            help='Tells Django to NOT prompt the user for input of any kind.',
        )
        parser.add_argument(
            '--list-groups',
            action='store_true',
            dest='list_groups',
            default=False,
            help='Output available groups for site update commands.',
        )
        parser.add_argument(
            'group',
            nargs='*',
            help='Specific group of update commands to run.',
        )

    @staticmethod
    def _get_command_instance(name):
        app_name = get_commands()[name]
        if isinstance(app_name, BaseCommand):
            return app_name
        else:
            return load_command_class(app_name, name)

    @staticmethod
    def _parse_cmd_specs(cmd_specs):
        parsed_cmd_specs = []
        for cmd_spec in cmd_specs:
            if isinstance(cmd_spec, six.string_types):
                cmd_opts = [cmd_spec, (), {}, None]
            elif isinstance(cmd_spec, (list, tuple)):
                cmd_opts = (list(cmd_spec) + [None, None, None, None])[:4]
                if not cmd_opts[0]:
                    raise CommandError('no command')
                cmd_opts[1] = cmd_opts[1] or ()
                cmd_opts[2] = cmd_opts[2] or {}
                if isinstance(cmd_opts[3], six.string_types):
                    cmd_opts[3] = [cmd_opts[3]]
            else:
                raise CommandError('unknown command spec')
            parsed_cmd_specs.append(cmd_opts)
        return parsed_cmd_specs

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        interactive = bool(options.get('interactive', True))
        list_groups = bool(options.get('list_groups', False))
        groups = options.get('group', None) or []
        site_update_commands = get_site_utils_setting('SITE_UPDATE_COMMANDS', merge_dicts=True)

        if not groups:
            if list_groups:
                groups = site_update_commands.keys()
            elif 'default' in site_update_commands:
                groups = ['default']
        for group in groups:
            if group not in site_update_commands:
                raise CommandError('Unknown group %s' % group)

        for group in groups:
            if verbosity >= 1 and list_groups:
                msg = '[{}]'.format(group)
                self.stdout.write(self.style.MIGRATE_HEADING(msg))
            elif verbosity >= 1 and not list_groups:
                msg = 'site_update: Running commands from group "{}".'.format(group)
                self.stdout.write(self.style.MIGRATE_HEADING('=' * len(msg.strip())))
                self.stdout.write(self.style.MIGRATE_HEADING(msg))
                self.stdout.write(self.style.MIGRATE_HEADING('=' * len(msg.strip())))
            cmd_specs = self._parse_cmd_specs(site_update_commands[group])
            for cmd_spec in cmd_specs:
                cmd_name = cmd_spec[0]
                cmd_args = cmd_spec[1]
                cmd_opts = cmd_spec[2]
                cmd_display_args = ['{!r}'.format(a) for a in cmd_args]
                cmd_display_args.extend(['{}={!r}'.format(k, v) for k, v in cmd_opts.items()])
                cmd_apps = cmd_spec[3] or []
                cmd_apps_missing = []
                for cmd_app in cmd_apps:
                    if not app_is_installed(cmd_app):
                        cmd_apps_missing.append(cmd_app)
                if list_groups:
                    if cmd_apps_missing:
                        cmd_skipped = ' (skipped: {} not installed)'.format(', '.join(cmd_apps_missing))
                    else:
                        cmd_skipped = ''
                    if verbosity >= 2:
                        msg = '{}({}){}'.format(cmd_name, ', '.join(cmd_display_args), cmd_skipped)
                        self.stdout.write(self.style.MIGRATE_LABEL(msg))
                else:
                    if cmd_apps_missing:
                        if verbosity >= 2:
                            msg = '\nsite_update: Skipping: {} ({} not installed).'.format(cmd_name, ', '.join(cmd_apps_missing))
                            self.stdout.write(self.style.WARNING(msg))
                        continue
                    if verbosity >= 1:
                        msg = '\nsite_update: Running {}({})'.format(cmd_name, ', '.join(cmd_display_args))
                        self.stdout.write(self.style.MIGRATE_LABEL(msg))
                        self.stdout.write(self.style.MIGRATE_LABEL('-' * len(msg.strip())))

                    # Check if command supports an "interactive" argument.
                    try:
                        cmd_instance = self._get_command_instance(cmd_name)
                    except KeyError:
                        raise CommandError('Unknown command: {!r}'.format(cmd_name))
                    cmd_parser = cmd_instance.create_parser('', cmd_name)
                    if bool('interactive' in [opt.dest for opt in cmd_parser._actions]):
                        cmd_opts.setdefault('interactive', interactive)
                    cmd_opts.setdefault('verbosity', verbosity)

                    # Prevent collectstatic from failing when the clear option is
                    # specified and the static root doesn't exist.
                    if cmd_name == 'collectstatic' and cmd_opts.get('clear', False):
                        if not os.path.exists(settings.STATIC_ROOT):
                            os.makedirs(settings.STATIC_ROOT)
                    call_command(cmd_name, *cmd_args, **cmd_opts)
