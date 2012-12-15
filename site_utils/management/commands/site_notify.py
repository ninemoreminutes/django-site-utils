# Python
from optparse import make_option

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

class Command(BaseCommand):
    """Management command to notify site admins/managers."""

    option_list = BaseCommand.option_list + (
        make_option('-a', '--admins', action='store_true', dest='admins',
            default=False, help=_('Notify all addresses in settings.ADMINS')),
        make_option('-m', '--managers', action='store_true', dest='managers',
            default=False, help=_('Notify all addresses in settings.MANAGERS')),
        make_option('-u', '--superusers', action='store_true', dest='superusers',
            default=False, help=_('Notify all users with superuser status')),
        make_option('-s', '--staff', action='store_true', dest='staff',
            default=False, help=_('Notify all users with staff status')),
        make_option('--bcc', action='store_true', dest='bcc',
            default=False, help=_('BCC all recipients')),
        make_option('--subject-template', action='store', dest='subject_template',
            default=None, help=_('Template to use for email subject.')),
        make_option('--body-template', action='store', dest='body_template',
            default=None, help=_('Template to use for email body.')),
    )
    args = _('[<subject> [<body> ...]]')
    help = _('Send a notification message to site admins/managers.')

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        admins = bool(options.get('admins', False))
        managers = bool(options.get('managers', False))
        superusers = bool(options.get('superusers', False))
        staff = bool(options.get('staff', False))
        # Default to only admins if no user options are specified.
        if not (admins or managers or superusers or staff):
            admins = True
        bcc = bool(options.get('bcc', False))
        subject_template = getattr(settings, 'SITE_NOTIFY_SUBJECT_TEMPLATE',
                                   'site_utils/site_notify_subject.txt')
        subject_template = options.get('subject_template', None) or subject_template
        body_template = getattr(settings, 'SITE_NOTIFY_BODY_TEMPLATE',
                                'site_utils/site_notify_body.txt')
        body_template = options.get('body_template', None) or body_template
        subject_text = args[0] if args else _('Site Notification')
        subject_context = {'subject': subject_text}
        subject = render_to_string(subject_template, subject_context)
        subject = ' '.join(filter(None, map(lambda x: x.strip(),
                                            subject.splitlines())))
        subject = settings.EMAIL_SUBJECT_PREFIX + subject
        body_sections = args[1:]
        body_text = '\n\n'.join(body_sections)
        body_context = {'body_sections': body_sections, 'body': body_text}
        body = render_to_string(body_template, body_context)
        recipients = {}
        if admins:
            for name, email in settings.ADMINS:
                recipients.setdefault(email, name)
        if managers:
            for name, email in settings.MANAGERS:
                recipients.setdefault(email, name)
        if superusers:
            for user in User.objects.filter(is_active=True, is_superuser=True):
                recipients.setdefault(email, name)
        if staff:
            for user in User.objects.filter(is_active=True, is_staff=True):
                recipients.setdefault(email, name)
        recipient_list = ['"%s" <%s>' % (v,k) for k,v in recipients.items()]
        email_options = {'subject': subject, 'body': body}
        email_options['bcc' if bcc else 'to'] = recipient_list
        email_message = EmailMessage(**email_options)
        email_message.send()
