# Python
from optparse import make_option
import os

# Django
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

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
        # Django-Extensions
        if 'django_extensions' in settings.INSTALLED_APPS:
            call_command('clean_pyc', verbosity=verbosity, optimize=True)
        # Database/South
        call_command('syncdb', verbosity=verbosity, interactive=interactive)
        call_command('migrate', verbosity=verbosity, interactive=interactive)
        call_command('update_permissions', verbosity=verbosity)
        # Expired sessions
        call_command('cleanup', verbosity=verbosity)
        # Registration
        if 'registration' in settings.INSTALLED_APPS:
            call_command('cleanupregistration', verbosity=verbosity)
        # Freebie (cleanup stale tables)
        call_command('sitecleanup', verbosity=verbosity)
        # Reversion
        #if 'reversion' in settings.INSTALLED_APPS:
        #    call_command('createinitialrevisions', verbosity=verbosity)
        # ExtAuth
        if 'freebie.apps.extauth2' in settings.INSTALLED_APPS:
            call_command('updateperms', verbosity=verbosity)
            call_command('updateroles', verbosity=verbosity)
        # FIXME: makemessages/compilemessages?
        # Staticfiles
        if not os.path.exists(settings.STATIC_ROOT):
            os.makedirs(settings.STATIC_ROOT)
        call_command('collectstatic', verbosity=verbosity, interactive=interactive, clear=True)
