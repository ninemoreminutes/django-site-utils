# Python
from optparse import make_option
import sys

# Django
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.utils.translation import ugettext_lazy as _

class Command(BaseCommand):
    """Cleanup unused database tables and content types."""

    option_list = BaseCommand.option_list + (
        make_option('-n', '--dry-run', action='store_true', dest='dry_run',
                    default=False, help='Dry run only.'),
    )
    help = 'Remove stale database tables and content types.'

    requires_model_validation = True

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        dry_run = options.get('dry_run', False)
        for ct in ContentType.objects.all():
            if ct.model_class():
                continue
            if verbosity >= 1:
                print >> sys.stdout, 'Removing %r' % ct
            if not dry_run:
                ct.delete()
        cursor = connection.cursor()
        all_tables = set(connection.introspection.table_names())
        django_tables = set(connection.introspection.django_table_names())
        for stale_table in (all_tables - django_tables):
            sql = 'DROP TABLE %s;' % stale_table
            if verbosity >= 1:
                print >> sys.stdout, 'Removing table %s' % stale_table
            if verbosity >= 2:
                print >> sys.stdout, sql
            if not dry_run:
                cursor.execute(sql)
