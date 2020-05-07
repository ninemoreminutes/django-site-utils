# flake8: noqa

# Python
from __future__ import unicode_literals
from collections import OrderedDict
import datetime
import os
import shutil
import tempfile
import zipfile

# Django
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
#from django.core.management.commands.dumpdata import sort_dependencies
from django.db import models
from django.db import router, DEFAULT_DB_ALIAS
#from django.db.models import get_apps, get_models, get_model, get_app
#from django.utils.datastructures import SortedDict

# Django-Site-Utils
from ...serializers import SiteSerializer


class Command(BaseCommand):
    """Dump the contents of the entire site, including media files."""

    help = 'Dump the contents of the entire site, including media files, to ' \
           'an archive containing a fixture of the given format.'

    def add_arguments(self, parser):
        parser.add_argument('-o', '--output', default=None, dest='output',
                    help='Specifies the output archive (ZIP) filename.')
        parser.add_argument('--database', action='store', dest='database',
                    default=DEFAULT_DB_ALIAS, help='Nominates a specific database to '
                    'dump fixtures from. Defaults to the "default" database.')
        parser.add_argument('-e', '--exclude', dest='exclude', action='append',
                    default=[], help='An appname or appname.ModelName to exclude (use '
                    'multiple --exclude to exclude multiple apps/models).')
        parser.add_argument('-a', '--all', action='store_true', dest='use_base_manager',
                    default=True, help='Use Django\'s base manager to dump all models '
                    'stored in the database, including those that would otherwise be '
                    'filtered or modified by a custom manager.')
        parser.add_argument('modelspec', nargs='*', metavar='appname.ModelName',
                            help='apps/models to dump')

    def build_app_dict(self, app_labels=[], excludes=[]):
        """Build dictionary of apps and models to dump."""
        # Determine excluded apps and models.
        excluded_model_classes = set()
        for exclude in excludes:
            if '.' in exclude:
                app_label, model_name = exclude.split('.', 1)
                model_class = apps.get_model(app_label, model_name)
                if not model_class:
                    raise CommandError('Unknown model in excludes: %s' % exclude)
                excluded_model_classes.add(model_class)
            else:
                try:
                    app_config = apps.get_app_config(exclude)
                    for model_class in app_config.get_models():
                        excluded_model_classes.add(model_class)
                except ImproperlyConfigured:
                    raise CommandError('Unknown app in excludes: %s' % exclude)
        # Build dictionary of apps (as keys) and a list of models (as values).
        if not app_labels:
            app_labels = [app_config.label for app_config in apps.get_app_configs()]
        app_list = OrderedDict()
        for label in app_labels:
            try:
                # App with model name.
                app_label, model_name = label.split('.', 1)
                model_class = apps.get_model(app_label, model_name)
                if not model_class:
                    raise CommandError('Unknown model: %s.%s' % (app_label, model_label))
                if model_class in excluded_model_classes:
                    continue
                app_list_model_classes = app_list.setdefault(app_label, [])
                if model_class not in app_list_model_classes:
                    app_list_model_classes.append(model_class)
            except ValueError:
                # App label only, with no model qualifier.
                app_label = label
                try:
                    app_config = apps.get_app_config(app_label)
                except ImproperlyConfigured:
                    raise CommandError('Unknown application: %s' % app_label)
                for model_class in app_config.get_models():
                    if model_class in excluded_model_classes:
                        continue
                    app_list_model_classes = app_list.setdefault(app_label, [])
                    if model_class not in app_list_model_classes:
                        app_list_model_classes.append(model_class)
        return app_list

    def save_file_field(self, obj, field, archive):
        """Save file field data to the given archive."""
        src = getattr(obj, field.name)
        if src.name:
            try:
                tf_path = None
                try:
                    file_path = src.path
                except NotImplementedError:
                    file_path = None
                if file_path is None:
                    src.open('rb')
                    tf_handle, tf_path = tempfile.mkstemp()
                    tf = os.fdopen(tf_handle, 'wb')
                    shutil.copyfileobj(src, tf)
                    src.close()
                    tf.close()
                    file_path = tf_path
                zip_path = 'site_media/%s' % src.name
                zip_path = zip_path.encode('ascii')
                archive.write(file_path, zip_path)
            finally:
                try:
                    if tf_path:
                        os.remove(tf_path)
                except:
                    pass

    def iter_objects(self, app_dict, using, use_base_manager=False, archive=None):
        """Iterate over all models from the given app dictionary."""
        for model in sort_dependencies(app_dict.items()):
            if not model._meta.proxy and router.allow_syncdb(using, model):
                file_fields = set()
                for field in model._meta.fields:
                    if isinstance(field, models.FileField):
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
        """Handle the site_dump management command."""
        # verbosity = int(options.get('verbosity', 1))
        output = options.get('output', None)
        if output is None:
            output = 'site_dump_%s.zip' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        using = options.get('database')
        excludes = options.get('exclude')
        show_traceback = options.get('traceback')
        use_base_manager = options.get('use_base_manager')
        app_dict = self.build_app_dict(app_labels, excludes)
        print(app_dict)
        return
        try:
            file_path = None
            archive = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
            object_iter = self.iter_objects(app_dict, using, use_base_manager,
                                            archive)
            file_handle, file_path = tempfile.mkstemp(suffix='.json',
                                                      prefix='site_dump_')
            datafile = os.fdopen(file_handle, 'wb')
            serializer = SiteSerializer()
            serializer.serialize(object_iter, indent=4, use_natural_keys=True,
                                 stream=datafile)
            datafile.close()
            archive.write(file_path, 'site_dump.json')
            archive.writestr('site_dump_version', '1')
            archive.close()
        except Exception as e:
            if 1 or show_traceback:
                raise
            raise CommandError('Unable to serialize database: %s' % e)
        finally:
            try:
                if file_path:
                    os.remove(file_path)
            except:
                pass
