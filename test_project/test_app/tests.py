# Python
import sys
import StringIO

# Django
from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.contrib.sites.models import Site

# Django-Site-Utils
from site_utils.utils import app_is_installed

class TestSiteUtils(TestCase):
    """Test cases for Site Utils management commands and utilities."""

    def _call_command(self, name, *args, **options):
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
        raise NotImplementedError

    def test_site_config(self):
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.com')
        self.assertEqual(site.domain, 'example.com')
        result = self._call_command('site_config', verbosity=0)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.com')
        self.assertEqual(site.domain, 'example.com')
        result = self._call_command('site_config', _name='example.net', verbosity=0)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.net')
        self.assertEqual(site.domain, 'example.com')
        result = self._call_command('site_config', domain='example.net', verbosity=0)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.net')
        self.assertEqual(site.domain, 'example.net')
        result = self._call_command('site_config', _name='example.org',
                                    domain='example.org', verbosity=0)
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
        #print result
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[-1]
        print msg, msg.to
        raise NotImplementedError

    def test_site_update(self):
        raise NotImplementedError
