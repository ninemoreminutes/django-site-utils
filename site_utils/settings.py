# Python
from __future__ import unicode_literals

# Django
from django.conf import settings
from django.utils.translation import gettext_lazy as _


DEFAULT_SITE_CLEANUP_FUNCTIONS = (
    'site_utils.cleanup.cleanup_stale_content_types',
    'site_utils.cleanup.cleanup_unused_database_tables',
)

DEFAULT_SITE_NOTIFY_DEFAULT_RECIPIENTS = ('admins',)

DEFAULT_SITE_NOTIFY_SUBJECT_TEMPLATE = 'site_utils/notify_subject.txt'

DEFAULT_SITE_NOTIFY_BODY_TEMPLATE = 'site_utils/notify_body.txt'

DEFAULT_SITE_UPDATE_COMMANDS = {
    'default': [
        'check',
        ('migrate', [], {'fake_initial': True}),
        ('collectstatic', [], {}, 'staticfiles'),
    ],
}

DEFAULT_SITE_ERROR_MESSAGES = {
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

DEFAULT_SITE_ERROR_TEMPLATES = [
    (r'', 'site_utils/error.html'),
]


def get_site_utils_setting(name, merge_dicts=False):
    try:
        default_setting = globals()['DEFAULT_{}'.format(name)]
        setting = getattr(settings, name, None)
        if merge_dicts:
            setting_dict = dict(default_setting.items())
            if setting:
                setting_dict.update(setting.items())
            return setting_dict
        else:
            return setting or default_setting
    except KeyError:
        raise RuntimeError('invalid setting name: {}'.format(name))
