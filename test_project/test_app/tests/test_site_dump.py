# flake8: noqa

# Python
from __future__ import unicode_literals
import datetime
import email.utils
import functools
import hashlib
import os
import shutil
import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import tempfile
import zipfile

# Py.Test
import pytest

# Django
from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.core.files.base import ContentFile
from django.core.management import get_commands, load_command_class, BaseCommand
from django.contrib.auth.models import User, Group, Permission
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.sites.models import Site
from django.db import connection, models
from django.urls import reverse
from django.utils.encoding import is_protected_type

# Django-Site-Utils
from site_utils import settings as defaults
from site_utils.serializers import SiteJsonEncoder
from site_utils.utils import app_is_installed

# Test App
from ..models import Document, Photo


def _call_site_dump(self, *app_labels, **options):
    options.setdefault('verbosity', 1)
    temp_dir = tempfile.mkdtemp()
    self._temp_dirs.append(temp_dir)
    os.chdir(temp_dir)
    result = self._call_command('site_dump', *app_labels, **options)
    self.assertEqual(result[0], None)
    output = options.get('output', None) or os.listdir(temp_dir)[0]
    if not os.path.isabs(output):
        output = os.path.join(temp_dir, output)
    return result, output

def _check_site_dump_file(self, output, only_models=None):
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
                    relobj = field.rel.to.objects.get_by_natural_key(*field_value)
                else:
                    relobj = field.rel.to.get(pk=field_value)
            else:
                value = getattr(obj, field_name)
                if not is_protected_type(value):
                    value = field.value_to_string(obj)
                if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                    # FIXME: Probably a better way, but this gets it done for now.
                    value = simplejson.loads(simplejson.dumps(value, cls=SiteJsonEncoder))
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

@pytest.mark.xfail()
def test_site_dump(self):
    # Test default with no options.
    result, output = self._call_site_dump()
    self._check_site_dump_file(output)
    # Create user/group data (adds many to many relation).
    group1 = Group.objects.create(name='GroupOne')
    group2 = Group.objects.create(name='GroupTwo')
    user = User.objects.create_superuser('superfred', 'fred@ixmm.net', 'fredsPASS')
    user.first_name = 'Super'
    user.last_name = 'Fred'
    user.save()
    user.groups.add(group1)
    user.groups.add(group2)
    result, output = self._call_site_dump()
    self._check_site_dump_file(output)
    # Create models with attached files (also date and time fields).
    document = Document.objects.create(title='Test Doc', created_by=user)
    document.doc.save('test.txt', ContentFile('this is some test stuff'))
    photo = Photo.objects.create(caption='Test Photo', created_by=user)
    photo.image.save('test.jpg', ContentFile('blah blah blah'))
    result, output = self._call_site_dump()
    self._check_site_dump_file(output)
    # Specify only certain apps/models.
    result, output = self._call_site_dump('test_app')
    self._check_site_dump_file(output, (Document, Photo))
    result, output = self._call_site_dump('test_app.Document')
    self._check_site_dump_file(output, (Document,))
    # Exclude specific apps/models.
    result, output = self._call_site_dump('auth', exclude=['auth.Permission'])
    self._check_site_dump_file(output, (User, Group))
    result, output = self._call_site_dump(exclude=['south', 'admin'])
    self._check_site_dump_file(output, (User, Group, Permission, ContentType,
                                        Site, Document, Photo))
    # Specify alternate output file name.
    result, output = self._call_site_dump(output='blah.zip')
    self.assertEqual(os.path.basename(output), 'blah.zip')
    self._check_site_dump_file(output)
    return output
