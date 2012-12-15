# Django
from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.contrib.sites.models import Site

class TestSiteUtils(TestCase):
    """Test cases for Site Utils management commands."""

    def test_site_cleanup(self):
        raise NotImplementedError

    def test_site_config(self):
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.com')
        self.assertEqual(site.domain, 'example.com')
        call_command('site_config', verbosity=0)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.com')
        self.assertEqual(site.domain, 'example.com')
        call_command('site_config', _name='example.net', verbosity=0)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.net')
        self.assertEqual(site.domain, 'example.com')
        call_command('site_config', domain='example.net', verbosity=0)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.net')
        self.assertEqual(site.domain, 'example.net')
        call_command('site_config', _name='example.org', domain='example.org',
                     verbosity=0)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.org')
        self.assertEqual(site.domain, 'example.org')

    def test_site_dump(self):
        raise NotImplementedError

    def test_site_load(self):
        raise NotImplementedError

    def test_site_notify(self):
        self.assertEqual(len(mail.outbox), 0)
        call_command('site_notify')
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[-1]
        print msg, msg.to
        raise NotImplementedError

    def test_site_update(self):
        raise NotImplementedError
