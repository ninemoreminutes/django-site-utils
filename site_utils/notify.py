# Python
from __future__ import unicode_literals
import collections

# Django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.test.client import RequestFactory
from django.utils.encoding import force_text

# Django-Site-Utils
from .settings import get_site_utils_setting
from .utils import auth_is_installed

__all__ = ['notify_users']


def notify_users(subject_text=None, body_text=None, all_users=False,
                 admins=False, managers=False, superusers=False, staff=False,
                 bcc=False, subject_template=None, body_template=None,
                 dry_run=False, request=None, **kwargs):
    """
    Send an email notification to selected site users.
    """
    # Determine which user types should be notified.
    admins = admins or all_users
    managers = managers or all_users
    if auth_is_installed():
        superusers = superusers or all_users
        staff = staff or all_users
        user_model = get_user_model()
    else:
        superusers = False
        staff = False
        user_model = None
    if not (admins or managers or superusers or staff):
        default_recipients = set(get_site_utils_setting('SITE_NOTIFY_DEFAULT_RECIPIENTS'))
        admins = 'admins' in default_recipients
        managers = 'managers' in default_recipients
        if auth_is_installed():
            superusers = 'superusers' in default_recipients
            staff = 'staff' in default_recipients

    # Build full list of recipients.
    recipients = collections.OrderedDict()
    if admins:
        for name, email in settings.ADMINS:
            recipients.setdefault(email, name)
    if managers:
        for name, email in settings.MANAGERS:
            recipients.setdefault(email, name)
    if superusers and user_model:
        for user in user_model.objects.filter(is_active=True, is_superuser=True):
            recipients.setdefault(user.email, user.get_full_name() or user.email)
    if staff and user_model:
        for user in user_model.objects.filter(is_active=True, is_staff=True):
            recipients.setdefault(user.email, user.get_full_name() or user.email)

    # Render subject and body of notification.
    # TODO: Future feature: render subject/body per recipient.
    subject_template = subject_template or get_site_utils_setting('SITE_NOTIFY_SUBJECT_TEMPLATE')
    body_template = body_template or get_site_utils_setting('SITE_NOTIFY_BODY_TEMPLATE')
    subject_text = subject_text if subject_text is not None else 'Site Notification'
    if isinstance(body_text, (list, tuple)):
        body_text = '\n\n'.join(body_text)
    context = dict(subject=subject_text, body=body_text)
    request = request or RequestFactory().get('/')
    subject = render_to_string(subject_template, context, request)
    subject = ' '.join(filter(None, map(lambda x: x.strip(), subject.splitlines())))
    subject = settings.EMAIL_SUBJECT_PREFIX + subject
    body = render_to_string(body_template, context, request)

    # Create and send the email.
    email_kwargs = dict(subject=subject, body=body)
    # FIXME: Sanitize user full name and email?
    email_recipients = ['"{}" <{}>'.format(v, k) for k, v in recipients.items()]
    email_kwargs['bcc' if bcc else 'to'] = email_recipients
    email_message = EmailMessage(**email_kwargs)
    if dry_run:
        print(force_text(email_message.message()))
    else:
        email_message.send()
