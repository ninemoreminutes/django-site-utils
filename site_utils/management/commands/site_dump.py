# Python
from optparse import make_option
import os
import shutil
import sys
import tempfile
import zipfile

# Django
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.dumpdata import sort_dependencies
from django.core import serializers
from django.db import models, transaction
from django.db import router, DEFAULT_DB_ALIAS
from django.db.models import get_apps, get_models, get_model, get_app
from django.utils.datastructures import SortedDict

# Django-Site-Utils
from site_utils.serializers import JsonSerializer

class Command(BaseCommand):
    """Dump the contents of the entire site, including media files."""

    option_list = BaseCommand.option_list + (
        make_option('-o', '--output', default='site_dump.zip', dest='output',
            help='Specifies the output archive filename.'),
        #make_option('--format', default='json', dest='format',
        #    help='Specifies the output serialization format for fixtures.'),
        #make_option('--indent', default=None, dest='indent', type='int',
        #    help='Specifies the indent level to use when pretty-printing output'),
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a specific database to dump '
                'fixtures from. Defaults to the "default" database.'),
        make_option('-e', '--exclude', dest='exclude', action='append', default=[],
            help='An appname or appname.ModelName to exclude (use multiple --exclude to exclude multiple apps/models).'),
        #make_option('-n', '--natural', action='store_true', dest='use_natural_keys', default=True,
        #    help='Use natural keys if they are available.'),
        make_option('-a', '--all', action='store_true', dest='use_base_manager', default=True,
            help='Use Django\'s base manager to dump all models stored in the database, including those that would otherwise be filtered or modified by a custom manager.'),
    )
    help = ('Dump the contents of the entire site, including media files, to an '
            'archive containing a fixture of the given format.')
    args = '[appname appname.ModelName ...]'

    def build_app_dict(self, app_labels=[], excludes=[]):
        """Build dictionary of apps and models to dump."""
        from django.db.models import get_app, get_apps, get_model, get_models

        # Determine excluded apps and models.
        excluded_apps = set()
        excluded_models = set()
        for exclude in excludes:
            if '.' in exclude:
                app_label, model_name = exclude.split('.', 1)
                model_obj = get_model(app_label, model_name)
                if not model_obj:
                    raise CommandError('Unknown model in excludes: %s' % exclude)
                excluded_models.add(model_obj)
            else:
                try:
                    app_obj = get_app(exclude)
                    excluded_apps.add(app_obj)
                except ImproperlyConfigured:
                    raise CommandError('Unknown app in excludes: %s' % exclude)

        # Build dictionary of apps (as keys) and a list of models (as values).
        if not app_labels:
            app_labels = [app.__name__.split('.')[-2] for app in get_apps()]
        app_list = SortedDict()
        for label in app_labels:
            print 'label', label
            try:
                app_label, model_label = label.split('.')
                try:
                    app = get_app(app_label)
                except ImproperlyConfigured:
                    raise CommandError("Unknown application: %s" % app_label)
                if app in excluded_apps:
                    continue
                model = get_model(app_label, model_label)
                if model is None:
                    raise CommandError("Unknown model: %s.%s" % (app_label, model_label))
                if model in excluded_models:
                    continue

                if app in app_list.keys():
                    if app_list[app] and model not in app_list[app]:
                        app_list[app].append(model)
                else:
                    app_list[app] = [model]
            except ValueError:
                # This is just an app - no model qualifier
                app_label = label
                try:
                    app = get_app(app_label)
                    print 'app', app
                except ImproperlyConfigured:
                    raise CommandError("Unknown application: %s" % app_label)
                if app in excluded_apps:
                    continue
                if app not in app_list.keys():
                    app_list[app] = []
                for model in get_models(app):
                    print 'model', model
                    if model in excluded_models:
                        continue
                    if model not in app_list[app]:
                        app_list[app].append(model)
        return app_list

    def save_file_field(self, obj, field, archive):
        src = getattr(obj, field.name)
        if src.name:
            print '   ', obj, field.name, src.name
            try:
                if src.path:
                    file_path = src.path
                else:
                    src.open('rb')
                    tf = tempfile.NamedTemporaryFile(delete=False)
                    shutil.copyfileobj(src, tf)
                    tf.close()
                    file_path = tf.name
                print file_path
                archive.write(file_path, 'site_media/%s' % src.name)
            finally:
                try:
                    os.remove(tf.name)
                except:
                    pass
        

    def iter_objects(self, app_dict, using, use_base_manager=False, archive=None):
        # Collate the objects to be serialized.
        for model in sort_dependencies(app_dict.items()):
            print model
            if not model._meta.proxy and router.allow_syncdb(using, model):

                file_fields = set()
                for field in model._meta.fields:
                    if isinstance(field, models.FileField):
                        print '   ', field.name
                        file_fields.add(field)

                if use_base_manager:
                    objects = model._base_manager
                else:
                    objects = model._default_manager
                for obj in objects.using(using).order_by(model._meta.pk.name).iterator():
                    yield obj
                    for field in file_fields:
                        self.save_file_field(obj, field, archive)



    def handle(self, *app_labels, **options):
        verbosity = int(options.get('verbosity', 1))
        output = options.get('output')
        format = 'json'#options.get('format')
        indent = 4#options.get('indent')
        using = options.get('database')
        excludes = options.get('exclude')
        show_traceback = options.get('traceback')
        use_natural_keys = True#options.get('use_natural_keys')
        use_base_manager = options.get('use_base_manager')

        app_dict = self.build_app_dict(app_labels, excludes)
        try:
            datafile = None
            archive = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
            objects = self.iter_objects(app_dict, using, use_base_manager,
                                            archive)
            datafile = tempfile.NamedTemporaryFile(suffix='.json',
                                                   prefix='site_dump_',
                                                   delete=False)
            serializer = JsonSerializer()
            serializer.serialize(objects, indent=indent,
                                 use_natural_keys=use_natural_keys,
                                 stream=datafile)
            datafile.close()
            file('_site_dump.json', 'wb').write(file(datafile.name, 'rb').read())
            archive.write(datafile.name, 'site_dump.json')
            archive.writestr('site_dump_version', '1')
            archive.close()
        except Exception, e:
            if show_traceback:
                raise
            raise CommandError('Unable to serialize database: %s' % e)
        finally:
            try:
                os.remove(datafile.name)
            except:
                pass
