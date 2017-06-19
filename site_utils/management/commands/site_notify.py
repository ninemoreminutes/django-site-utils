# Django
from django.core.management.base import BaseCommand

# Django-Site-Utils
from site_utils.notify import notify_users
from site_utils.utils import auth_is_installed


class Command(BaseCommand):
    """
    Management command to notify site admins/managers.
    """

    help = 'Send a notification message to site admins/managers.'

    def add_arguments(self, parser):
        parser.add_argument('subject_text', nargs='?', metavar='subject')
        parser.add_argument('body_text', nargs='*', metavar='body')
        parser.add_argument('-a', '--admins', action='store_true', dest='admins', default=False,
                            help='Notify all addresses in settings.ADMINS.')
        parser.add_argument('-m', '--managers', action='store_true', dest='managers', default=False,
                            help='Notify all addresses in settings.MANAGERS.')
        if auth_is_installed():
            parser.add_argument('-u', '--superusers', action='store_true', dest='superusers', default=False,
                                help='Notify all active users with is_superuser status.')
            parser.add_argument('-s', '--staff', action='store_true', dest='staff', default=False,
                                help='Notify all active users with is_staff status.')
            parser.add_argument('--all', action='store_true', dest='all_users', default=False,
                                help='Notify all admins, managers, superusers and staff.')
        else:
            parser.add_argument('--all', action='store_true', dest='all_users', default=False,
                                help='Notify all admins and managers.')
        # TODO: Implement below.
        # parser.add_argument('--seperate', action='store_true',
        #                     dest='seperate', default=False, help='Send a separate notification to each recipient.')
        parser.add_argument('--bcc', action='store_true', dest='bcc', default=False,
                            help='BCC all recipients.')

    def handle(self, *args, **options):
        notify_users(**options)
