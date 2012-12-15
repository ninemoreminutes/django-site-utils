# Python
from optparse import make_option
import os
import shutil
import sys
import tempfile

# Django
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.dumpdata import sort_dependencies
from django.core import serializers
from django.db import models, transaction
from django.db import router, DEFAULT_DB_ALIAS
from django.db.models import get_apps, get_models
from django.utils.datastructures import SortedDict

class Command(BaseCommand):
    """Dump the contents of the entire site, including media files."""

    option_list = BaseCommand.option_list + (
        make_option('-o', '--output', default='dumpsite.zip', dest='output',
            help='Specifies the output archive filename.'),
        make_option('--format', default='json', dest='format',
            help='Specifies the output serialization format for fixtures.'),
        make_option('--indent', default=None, dest='indent', type='int',
            help='Specifies the indent level to use when pretty-printing output'),
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a specific database to dump '
                'fixtures from. Defaults to the "default" database.'),
        make_option('-e', '--exclude', dest='exclude',action='append', default=[],
            help='An appname or appname.ModelName to exclude (use multiple --exclude to exclude multiple apps/models).'),
        make_option('-n', '--natural', action='store_true', dest='use_natural_keys', default=True,
            help='Use natural keys if they are available.'),
        make_option('-a', '--all', action='store_true', dest='use_base_manager', default=True,
            help='Use Django\'s base manager to dump all models stored in the database, including those that would otherwise be filtered or modified by a custom manager.'),
    )
    help = ('Dump the contents of the entire site, including media files, to an '
            'archive containing a fixture of the given format.')
    args = '[appname appname.ModelName ...]'

    def handle(self, *app_labels, **options):
        from django.db.models import get_app, get_apps, get_model
        verbosity = int(options.get('verbosity', 1))
        output = options.get('output')
        format = options.get('format')
        indent = options.get('indent')
        using = options.get('database')
        excludes = options.get('exclude')
        show_traceback = options.get('traceback')
        use_natural_keys = options.get('use_natural_keys')
        use_base_manager = options.get('use_base_manager')

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

        if len(app_labels) == 0:
            app_list = SortedDict((app, None) for app in get_apps() if app not in excluded_apps)
        else:
            app_list = SortedDict()
            for label in app_labels:
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
                    except ImproperlyConfigured:
                        raise CommandError("Unknown application: %s" % app_label)
                    if app in excluded_apps:
                        continue
                    app_list[app] = None

        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        if format not in serializers.get_public_serializer_formats():
            raise CommandError("Unknown serialization format: %s" % format)

        try:
            serializers.get_serializer(format)
        except KeyError:
            raise CommandError("Unknown serialization format: %s" % format)

        # Now collate the objects to be serialized.
        objects = []
        for model in sort_dependencies(app_list.items()):
            if model in excluded_models:
                continue
            if not model._meta.proxy and router.allow_syncdb(using, model):
                if use_base_manager:
                    qs = model._base_manager.using(using).all()
                else:
                    qs = model._default_manager.using(using).all()
                objects.extend(qs)
                file_fields = set()
                for field in model._meta.fields:
                    if isinstance(field, models.FileField):
                        print '   ', field.name
                        file_fields.add(field)
                if file_fields:
                    for obj in qs:
                        for field in file_fields:
                            src = getattr(obj, field.name)
                            if src.name:
                                print '   ', obj, field.name, src.name


        
        try:
            serialized_data = serializers.serialize(format, objects, indent=indent,
                        use_natural_keys=use_natural_keys)
        except Exception, e:
            if show_traceback:
                raise
            raise CommandError("Unable to serialize database: %s" % e)

        if 0:
            for app in get_apps():
                for model in get_models(app):
                    print model
                    file_fields = []
                    for field in model._meta.fields:
                        if isinstance(field, models.FileField):
                            print '   ', field.name
                            file_fields.append(field)
                    if file_fields:
                        for obj in model.objects.all():
                            #print obj
                            for field in file_fields:
                                src = getattr(obj, field.name)
                                if src.name:
                                    print '   ', obj, field, src.name
                                if 0 and src:
                                    if not os.path.exists(os.path.dirname(os.path.join(os.path.dirname(__file__), 'backup', src.name))):
                                        os.makedirs(os.path.dirname(os.path.join(os.path.dirname(__file__), 'backup', src.name)))
                                    try:
                                    #if os.path.exists(os.path.join(MEDIA_ROOT, src.path)):
                                        shutil.copy(os.path.join(settings.MEDIA_ROOT, src.path), os.path.join(os.path.dirname(__file__), 'backup', src.name))
                                    except:
                                        print field.name, src
