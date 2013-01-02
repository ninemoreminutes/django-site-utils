# Python
from optparse import make_option

# Django
from django.conf import settings
from django.core.management.base import BaseCommand

# Django-Site-Utils
from site_utils.defaults import SITE_CLEANUP_FUNCTIONS

class Command(BaseCommand):
    """Run various functions to cleanup the site."""

    option_list = BaseCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('-n', '--dry-run', action='store_true', dest='dry_run',
                    default=False, help='Dry run only.'),
    )
    help = 'Run site cleanup functions.'

    requires_model_validation = True

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        site_cleanup_functions = []
        for func_spec in getattr(settings, 'SITE_CLEANUP_FUNCTIONS',
                                 SITE_CLEANUP_FUNCTIONS):
            module_name = func_spec.rsplit('.', 1)[0]
            func_name = func_spec.rsplit('.', 1)[1]
            module = __import__(module_name, fromlist=[func_name])
            func = getattr(module, func_name)
            site_cleanup_functions.append(func)
        for func in site_cleanup_functions:
            if verbosity >= 2:
                print 'Running site cleanup function "%s"' % func.__name__
            func(**options)
