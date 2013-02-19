# Python
import datetime
from optparse import make_option
import os
import shutil
import tempfile
import zipfile

# Django
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.dumpdata import sort_dependencies
from django.db import models
from django.db import router, DEFAULT_DB_ALIAS
from django.db.models import get_apps, get_models, get_model, get_app
from django.utils.datastructures import SortedDict

# Django-Site-Utils
from site_utils.serializers import JsonSerializer

class Command(BaseCommand):
    """Dump the contents of the entire site, including media files."""

    option_list = BaseCommand.option_list + (
        make_option('-o', '--output', default=None, dest='output',
            help='Specifies the output archive (ZIP) filename.'),
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a specific database to '
                'dump fixtures from. Defaults to the "default" database.'),
        make_option('-e', '--exclude', dest='exclude', action='append',
            default=[], help='An appname or appname.ModelName to exclude (use '
            'multiple --exclude to exclude multiple apps/models).'),
        make_option('-a', '--all', action='store_true', dest='use_base_manager',
            default=True, help='Use Django\'s base manager to dump all models '
            'stored in the database, including those that would otherwise be '
            'filtered or modified by a custom manager.'),
    )
    help = ('Dump the contents of the entire site, including media files, to '
            'an archive containing a fixture of the given format.')
    args = '[appname appname.ModelName ...]'

    def build_app_dict(self, app_labels=[], excludes=[]):
        """Build dictionary of apps and models to dump."""
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
            try:
                # App with model name.
                app_label, model_label = label.split('.')
                try:
                    app = get_app(app_label)
                except ImproperlyConfigured:
                    raise CommandError('Unknown application: %s' % app_label)
                if app in excluded_apps:
                    continue
                model = get_model(app_label, model_label)
                if model is None:
                    raise CommandError('Unknown model: %s.%s' % (app_label, model_label))
                if model in excluded_models:
                    continue
                if app in app_list.keys():
                    if app_list[app] and model not in app_list[app]:
                        app_list[app].append(model)
                else:
                    app_list[app] = [model]
            except ValueError:
                # App label only, with no model qualifier.
                app_label = label
                try:
                    app = get_app(app_label)
                except ImproperlyConfigured:
                    raise CommandError('Unknown application: %s' % app_label)
                if app in excluded_apps:
                    continue
                if app not in app_list.keys():
                    app_list[app] = []
                for model in get_models(app):
                    if model in excluded_models:
                        continue
                    if model not in app_list[app]:
                        app_list[app].append(model)
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
        verbosity = int(options.get('verbosity', 1))
        output = options.get('output', None)
        if output is None:
            output = 'site_dump_%s.zip' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        using = options.get('database')
        excludes = options.get('exclude')
        show_traceback = options.get('traceback')
        use_base_manager = options.get('use_base_manager')
        app_dict = self.build_app_dict(app_labels, excludes)
        try:
            file_path = None
            archive = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
            object_iter = self.iter_objects(app_dict, using, use_base_manager,
                                            archive)
            file_handle, file_path = tempfile.mkstemp(suffix='.json',
                                                      prefix='site_dump_')
            datafile = os.fdopen(file_handle, 'wb')
            serializer = JsonSerializer()
            serializer.serialize(object_iter, indent=4, use_natural_keys=True,
                                 stream=datafile)
            datafile.close()
            archive.write(file_path, 'site_dump.json')
            archive.writestr('site_dump_version', '1')
            archive.close()
        except Exception, e:
            if 1 or show_traceback:
                raise
            raise CommandError('Unable to serialize database: %s' % e)
        finally:
            try:
                if file_path:
                    os.remove(file_path)
            except:
                pass
