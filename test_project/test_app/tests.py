# Python
import sys
import StringIO

# Django
from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import connection

# Django-Site-Utils
from site_utils.utils import app_is_installed

class TestSiteUtils(TestCase):
    """Test cases for Site Utils management commands and utilities."""

    def _call_command(self, name, *args, **options):
        options.setdefault('verbosity', 0)
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        result = None
        try:
            result = call_command(name, *args, **options)
        except Exception, e:
            result = e
        finally:
            captured_stdout = sys.stdout.getvalue()
            captured_stderr = sys.stderr.getvalue()
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        return result, captured_stdout, captured_stderr

    def test_app_is_installed(self):
        self.assertTrue(app_is_installed('contenttypes'))
        self.assertTrue(app_is_installed('django.contrib.contenttypes'))
        self.assertTrue(app_is_installed('admin'))
        self.assertTrue(app_is_installed('django.contrib.admin'))
        self.assertFalse(app_is_installed('flatpages'))
        self.assertFalse(app_is_installed('django.contrib.flatpages'))
        self.assertTrue(app_is_installed('site_utils'))

    def test_site_cleanup(self):
        self.assertEqual(ContentType.objects.filter(app_label='myapp').count(), 0)
        newct = ContentType.objects.create(name='MyAppModel', app_label='myapp',
                                           model='mymodel')
        self.assertEqual(ContentType.objects.filter(app_label='myapp').count(), 1)
        all_tables = set(connection.introspection.table_names())
        self.assertFalse('myapp_othermodel' in all_tables)
        cursor = connection.cursor()
        sql = '''CREATE TABLE myapp_othermodel (id INTEGER PRIMARY KEY);'''
        cursor.execute(sql)
        all_tables = set(connection.introspection.table_names())
        self.assertTrue('myapp_othermodel' in all_tables)
        result = self._call_command('site_cleanup', dry_run=True)
        self.assertEqual(result[0], None)
        self.assertEqual(ContentType.objects.filter(app_label='myapp').count(), 1)
        all_tables = set(connection.introspection.table_names())
        self.assertTrue('myapp_othermodel' in all_tables)
        result = self._call_command('site_cleanup')
        self.assertEqual(result[0], None)
        self.assertEqual(ContentType.objects.filter(app_label='myapp').count(), 0)
        all_tables = set(connection.introspection.table_names())
        self.assertFalse('myapp_othermodel' in all_tables)

    def test_site_config(self):
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.com')
        self.assertEqual(site.domain, 'example.com')
        result = self._call_command('site_config')
        self.assertEqual(result[0], None)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.com')
        self.assertEqual(site.domain, 'example.com')
        result = self._call_command('site_config', _name='example.net')
        self.assertEqual(result[0], None)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.net')
        self.assertEqual(site.domain, 'example.com')
        result = self._call_command('site_config', domain='example.net')
        self.assertEqual(result[0], None)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.net')
        self.assertEqual(site.domain, 'example.net')
        result = self._call_command('site_config', _name='example.org',
                                    domain='example.org')
        self.assertEqual(result[0], None)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.org')
        self.assertEqual(site.domain, 'example.org')

    def test_site_dump(self):
        raise NotImplementedError

    def test_site_load(self):
        raise NotImplementedError

    def test_site_notify(self):
        
        self.assertEqual(len(mail.outbox), 0)
        result = self._call_command('site_notify')
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[-1]
        print msg, msg.to, msg.message()
        raise NotImplementedError

    def test_site_update(self):
        raise NotImplementedError
