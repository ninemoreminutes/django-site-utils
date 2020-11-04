# Python
from __future__ import unicode_literals

# Django
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string

# Django-Site-Utils
from ...settings import get_site_utils_setting


class Command(BaseCommand):

    help = 'Run site cleanup functions.'

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
            '-n',
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Dry run; only show what changes would be made.',
        )

    def handle(self, *args, **options):
        options['_command'] = self
        verbosity = int(options.get('verbosity', 1))
        site_cleanup_functions = []
        for func_import in get_site_utils_setting('SITE_CLEANUP_FUNCTIONS'):
            site_cleanup_functions.append(import_string(func_import))
        # FIXME: Honor interactive option and prompt before each function.
        for func in site_cleanup_functions:
            if verbosity >= 2:
                self.stdout.write('Running site cleanup function "{}"'.format(func.__name__))
            func(**options)
