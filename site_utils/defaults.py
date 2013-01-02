SITE_CLEANUP_FUNCTIONS = (
    'site_utils.utils.remove_stale_content_types',
    'site_utils.utils.remove_unused_database_tables',
)

SITE_NOTIFY_DEFAULT_RECIPIENTS = ('admins',)

SITE_NOTIFY_SUBJECT_TEMPLATE = 'site_utils/site_notify_subject.txt'

SITE_NOTIFY_BODY_TEMPLATE = 'site_utils/site_notify_body.txt'

SITE_UPDATE_COMMANDS = {
    'default': [
        'syncdb',
        ('migrate', [], {}, 'south'),
        ('collectstatic', [], {}, 'staticfiles'),
    ]
}
