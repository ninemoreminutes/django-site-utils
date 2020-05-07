# Python
from __future__ import unicode_literals

# Django
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import connection


def cleanup_stale_content_types(**options):
    """
    Remove state content types.
    """
    command = options.get('_command', None)
    verbosity = int(options.get('verbosity', 1))
    dry_run = bool(options.get('dry_run', False))
    if apps.is_installed('django.contrib.contenttypes'):
        for content_type in ContentType.objects.all():
            if content_type.model_class():
                continue
            if verbosity >= 1 and command:
                command.stdout.write('Removing {!r}\n'.format(content_type))
            if not dry_run:
                content_type.delete()


def cleanup_unused_database_tables(**options):
    """
    Remove unused database tables.
    """
    command = options.get('_command', None)
    verbosity = int(options.get('verbosity', 1))
    dry_run = bool(options.get('dry_run', False))
    cursor = connection.cursor()
    all_tables = set(connection.introspection.table_names())
    django_tables = set(connection.introspection.django_table_names())
    for stale_table in (all_tables - django_tables):
        sql = 'DROP TABLE %s;' % stale_table
        if verbosity >= 1 and command:
            command.stdout.write('Removing table {}\n'.format(stale_table))
        if verbosity >= 2:
            command.stdout.write('{}\n'.format(sql))
        if not dry_run:
            cursor.execute(sql)
