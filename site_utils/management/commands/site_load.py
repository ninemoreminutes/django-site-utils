# Python
import sys
import zipfile
from optparse import make_option
import traceback

# Django
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core import serializers
from django.core.management.color import no_style
from django.db import (connections, router, DEFAULT_DB_ALIAS,
      IntegrityError, DatabaseError)
from django.utils.itercompat import product

try:
    import bz2
    has_bz2 = True
except ImportError:
    has_bz2 = False


class Command(BaseCommand):
    """Load the contents of a site from a site_dump backup."""

    help = 'Installs the named fixture(s) in the database.'
    args = "fixture [fixture ...]"

    option_list = BaseCommand.option_list + (
        make_option('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS, help='Nominates a specific '
                    'database to load fixtures into. Defaults to the "default" '
                    'database.'),
    )

    def handle(self, *dump_files, **options):
        verbosity = int(options.get('verbosity'))
        show_traceback = options.get('traceback')
        using = options.get('database')
        connection = connections[using]

        if not dump_files:
            print >> sys.stderr, 'No site dump archives specified.  Please provide the path of at least one on the command line.'
            return

        # commit is a stealth option - it isn't really useful as
        # a command line option, but it can be useful when invoking
        # loaddata from within another script.
        # If commit=True, loaddata will use its own transaction;
        # if commit=False, the data load SQL will become part of
        # the transaction in place when loaddata was invoked.
        commit = options.get('commit', True)

        # Keep a count of the installed objects and fixtures
        fixture_count = 0
        loaded_object_count = 0
        fixture_object_count = 0
        models = set()

        humanize = lambda dirname: "'%s'" % dirname if dirname else 'absolute path'

        # Get a cursor (even though we don't need one yet). This has
        # the side effect of initializing the test database (if
        # it isn't already initialized).
        cursor = connection.cursor()

        # Start transaction management. All fixtures are installed in a
        # single transaction to ensure that all references are resolved.
        if commit:
            transaction.commit_unless_managed(using=using)
            transaction.enter_transaction_management(using=using)
            transaction.managed(True, using=using)

        try:
            with connection.constraint_checks_disabled():
                for dump_file in dump_files:
                    
                    archive = zipfile.ZipFile(dump_file, 'r')
                    version = archive.read('site_dump_version')
                    if version == '1':
                        objects = serializers.deserialize(format, fixture, using=using)

                        for obj in objects:
                            objects_in_fixture += 1
                            if router.allow_syncdb(using, obj.object.__class__):
                                loaded_objects_in_fixture += 1
                                models.add(obj.object.__class__)
                                try:
                                    obj.save(using=using)
                                except (DatabaseError, IntegrityError), e:
                                    msg = "Could not load %(app_label)s.%(object_name)s(pk=%(pk)s): %(error_msg)s" % {
                                            'app_label': obj.object._meta.app_label,
                                            'object_name': obj.object._meta.object_name,
                                            'pk': obj.object.pk,
                                            'error_msg': e
                                        }
                                    raise e.__class__, e.__class__(msg), sys.exc_info()[2]

                        loaded_object_count += loaded_objects_in_fixture
                        fixture_object_count += objects_in_fixture
                        label_found = True

                        # If the fixture we loaded contains 0 objects, assume that an
                        # error was encountered during fixture loading.
                        if objects_in_fixture == 0:
                            self.stderr.write(
                                self.style.ERROR("No fixture data found for '%s'. (File format may be invalid.)\n" %
                                    (fixture_name)))
                            if commit:
                                transaction.rollback(using=using)
                                transaction.leave_transaction_management(using=using)
                            return
                    else:
                        raise CommandError('unsupported version')


            # Since we disabled constraint checks, we must manually check for
            # any invalid keys that might have been added
            table_names = [model._meta.db_table for model in models]
            connection.check_constraints(table_names=table_names)

        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            if commit:
                transaction.rollback(using=using)
                transaction.leave_transaction_management(using=using)
            if show_traceback:
                traceback.print_exc()
            else:
                self.stderr.write(
                    self.style.ERROR("Problem installing fixture '%s': %s\n" %
                         (full_path, ''.join(traceback.format_exception(sys.exc_type,
                             sys.exc_value, sys.exc_traceback)))))
            return


        # If we found even one object in a fixture, we need to reset the
        # database sequences.
        if loaded_object_count > 0:
            sequence_sql = connection.ops.sequence_reset_sql(self.style, models)
            if sequence_sql:
                if verbosity >= 2:
                    self.stdout.write("Resetting sequences\n")
                for line in sequence_sql:
                    cursor.execute(line)

        if commit:
            transaction.commit(using=using)
            transaction.leave_transaction_management(using=using)

        if verbosity >= 1:
            if fixture_object_count == loaded_object_count:
                self.stdout.write("Installed %d object(s) from %d fixture(s)\n" % (
                    loaded_object_count, fixture_count))
            else:
                self.stdout.write("Installed %d object(s) (of %d) from %d fixture(s)\n" % (
                    loaded_object_count, fixture_object_count, fixture_count))

        # Close the DB connection. This is required as a workaround for an
        # edge case in MySQL: if the same connection is used to
        # create tables, load data, and query, the query can return
        # incorrect results. See Django #7572, MySQL #37735.
        if commit:
            connection.close()

    @transaction.commit_on_success
    def handle2(self, *args, **options):
        raise NotImplementedError # FIXME

        only_models = set(only_models or [])
        seen_models = set()
        archive = zipfile.ZipFile(output, 'r')
        version = archive.read('site_dump_version')
        self.assertEqual(version, '1')
        jsondata = archive.read('site_dump.json')
        data = simplejson.loads(jsondata)
        for objdict in data:
            model = get_model(*objdict['model'].split('.'))
            if only_models:
                self.assertTrue(model in only_models)
            seen_models.add(model)
            obj = model.objects.get(pk=objdict['pk'])
            if 'nk' in objdict:
                obj = model.objects.get_by_natural_key(*objdict['nk'])
            for field_name, field_value in objdict['fields'].items():
                field = obj._meta.get_field(field_name)
                if field in obj._meta.many_to_many:
                    for value in field_value:
                        if isinstance(value, (list, tuple)):
                            relobj = field.rel.to.objects.get_by_natural_key(*value)
                        else:
                            relobj = field.rel.to.get(pk=value)
                elif field.rel:
                    if isinstance(field_value, (list, tuple)):
                        if field_value and isinstance(field_value[0], (list, tuple)):
                            value = field_value[0]
                        else:
                            value = field_value
                        relobj = field.rel.to.objects.get_by_natural_key(*value)
                    else:
                        relobj = field.rel.to.get(pk=field_value)
                else:
                    value = getattr(obj, field_name)
                    if not is_protected_type(value):
                        value = field.value_to_string(obj)
                    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                        # FIXME: Probably a better way, but this gets it done for now.
                        value = simplejson.loads(simplejson.dumps(value, cls=DjangoJSONEncoder))
                    if isinstance(field, models.FileField):
                        field_file = getattr(obj, field_name)
                        field_file.open('rb')
                        file_md5 = hashlib.md5()
                        while True:
                            data = field_file.read(2**17)
                            if not data:
                                break
                            file_md5.update(data)
                        archive_name = 'site_media/%s' % value
                        if hasattr(archive, 'open'):
                            archive_file = archive.open(archive_name, 'r')
                        else:
                            archive_file = StringIO.StringIO(archive.read(archive_name))
                        archive_md5 = hashlib.md5()
                        while True:
                            data = archive_file.read(2**17)
                            if not data:
                                break
                            archive_md5.update(data)
                        self.assertEqual(file_md5.hexdigest(), archive_md5.hexdigest())
                    self.assertEqual(value, field_value)
        if only_models:
            self.assertEqual(only_models, seen_models)
