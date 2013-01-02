# Python
from optparse import make_option
import os

# Django
from django.core.management.base import BaseCommand
from django.core.management import call_command, CommandError
from django.conf import settings

# Django-Site-Utils
from site_utils.utils import app_is_installed
from site_utils.defaults import SITE_UPDATE_COMMANDS

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
    )

    help = 'Execute all management commands for a normal code/database update.'

    requires_model_validation = False

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        interactive = bool(options.get('interactive', True))
        site_update_commands = getattr(settings, 'SITE_UPDATE_COMMANDS',
                                       SITE_UPDATE_COMMANDS)
        if not args:
            args = ('default',)
        for arg in args:
            if arg not in site_update_commands:
                raise CommandError, 'unknown subcommand %s' % arg

        for arg in args:
            if verbosity >= 2:
                print 'Running site_update commands from group "%s"' % arg
            for cmd_spec in site_update_commands[arg]:
                if isinstance(cmd_spec, basestring):
                    cmd_opts = [cmd_spec, (), {}, None]
                elif isinstance(cmd_spec, (list, tuple)):
                    cmd_opts = (list(cmd_spec) + [None, None, None, None])[:4]
                    if not cmd_opts[0]:
                        raise CommandError, 'no command'
                    cmd_opts[1] = cmd_opts[1] or ()
                    cmd_opts[2] = cmd_opts[2] or {}
                    if isinstance(cmd_opts[3], basestring):
                        cmd_opts[3] = [cmd_opts[3]]
                else:
                    raise CommandError, 'unknown command spec'
                cmd_name = cmd_opts[0]
                cmd_args = cmd_opts[1]
                cmd_options = dict(verbosity=verbosity, interactive=interactive)
                cmd_options.update(cmd_opts[2])
                if not all([app_is_installed(x) for x in cmd_opts[3] or ()]):
                    if verbosity >= 2:
                        print 'Skipping commond "%s"' % cmd_name
                    continue
                if verbosity >= 2:
                    print 'Running command "%s" with args %r and options %r' % (cmd_name, cmd_args, cmd_options)
                call_command(cmd_name, *cmd_args, **cmd_options)
