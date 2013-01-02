# Django
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.db.models import get_app

__all__ = ['app_is_installed']

def app_is_installed(app_label):
    """Determine whether the given app is currently installed."""
    try:
        app = get_app(app_label.split('.')[-1])
        return True
    except ImproperlyConfigured:
        return False

def remove_stale_content_types(**options):
    """Remove state content types."""
    verbosity = int(options.get('verbosity', 1))
    dry_run = bool(options.get('dry_run', False))
    if app_is_installed('django.contrib.contenttypes'):
        from django.contrib.contenttypes.models import ContentType
        for ct in ContentType.objects.all():
            if ct.model_class():
                continue
            if verbosity >= 1:
                print 'Removing %r' % ct
            if not dry_run:
                ct.delete()

def remove_unused_database_tables(**options):
    """Remove unused database tables."""
    verbosity = int(options.get('verbosity', 1))
    dry_run = bool(options.get('dry_run', False))
    cursor = connection.cursor()
    all_tables = set(connection.introspection.table_names())
    django_tables = set(connection.introspection.django_table_names())
    for stale_table in (all_tables - django_tables):
        sql = 'DROP TABLE %s;' % stale_table
        if verbosity >= 1:
            print 'Removing table %s' % stale_table
        if verbosity >= 2:
            print sql
        if not dry_run:
            cursor.execute(sql)
