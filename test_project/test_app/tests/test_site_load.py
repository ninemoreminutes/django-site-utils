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


@pytest.mark.xfail()
def test_site_load(self):
    result, output = _call_site_dump(output='testload.zip')
    result = self._call_command('site_load', output)
    self.assertEqual(result[0], None)

    raise NotImplementedError
