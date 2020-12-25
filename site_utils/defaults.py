# Python
from __future__ import unicode_literals

# Django
from django.utils.translation import gettext_lazy as _


SITE_CLEANUP_FUNCTIONS = (
    'site_utils.cleanup.cleanup_stale_content_types',
    'site_utils.cleanup.cleanup_unused_database_tables',
)

SITE_NOTIFY_DEFAULT_RECIPIENTS = ('admins',)

SITE_NOTIFY_SUBJECT_TEMPLATE = 'site_utils/notify_subject.txt'

SITE_NOTIFY_BODY_TEMPLATE = 'site_utils/notify_body.txt'

SITE_UPDATE_COMMANDS = {
    'default': [
        'check',
        ('migrate', [], {'fake_initial': True}),
        ('collectstatic', [], {}, 'staticfiles'),
    ],
}

SITE_ERROR_MESSAGES = {
    400: (
        _('Bad Request'),
        _('The request could not be understood by the server.'),
    ),
    403: (
        _('Forbidden'),
        _('You do not have permission to access the requested resource.'),
    ),
    404: (
        _('Not Found'),
        _('The requested page could not be found.'),
    ),
    500: (
        _('Server Error'),
        _('An internal server error has occurred.'),
    ),
    502: (
        _('Bad Gateway'),
        _('An invalid response was received from the upstream server.'),
    ),
    503: (
        _('Server Unavailable'),
        _('The server is currently unavailable.'),
    ),
    504: (
        _('Gateway Timeout'),
        _('Did not receive a timely response from the upstream server.'),
    ),
}

SITE_ERROR_TEMPLATES = [
    (r'', 'site_utils/error.html'),
]

SITE_PATCHES = (
    'site_utils.patches.patch_runserver_addrport',
    'site_utils.patches.patch_wsgi_handler_keep_alive',
)
