# Python
import email.utils
import functools
import sys
import StringIO

# Django
from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.core.management import get_commands, load_command_class, BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import connection

# Django-Site-Utils
from site_utils import defaults
from site_utils.utils import app_is_installed

# From: http://stackoverflow.com/questions/9882280/find-out-if-a-function-has-been-called
def trackcalls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.has_been_called = True
        return func(*args, **kwargs)
    wrapper.has_been_called = False
    return wrapper

@trackcalls
def site_cleanup_function(**options):
    pass

class TestSiteUtils(TestCase):
    """Test cases for Site Utils management commands and utilities."""

    def setUp(self):
        super(TestSiteUtils, self).setUp()
        self._saved_settings = {}
        for attr in dir(settings):
            if attr == attr.upper():
                self._saved_settings[attr] = getattr(settings, attr)

    def tearDown(self):
        super(TestSiteUtils, self).tearDown()
        for attr in dir(settings):
            if attr == attr.upper() and attr not in self._saved_settings:
                #print 'delete', attr
                delattr(settings, attr)
        for attr, value in self._saved_settings.items():
            if getattr(settings, attr, None) != value:
                #print attr, value
                setattr(settings, attr, value)

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
        except SystemExit, e:
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
        # Create dummy content type.
        self.assertEqual(ContentType.objects.filter(app_label='myapp').count(), 0)
        newct = ContentType.objects.create(name='MyAppModel', app_label='myapp',
                                           model='mymodel')
        self.assertEqual(ContentType.objects.filter(app_label='myapp').count(), 1)
        # Create extra database table.
        all_tables = set(connection.introspection.table_names())
        self.assertFalse('myapp_othermodel' in all_tables)
        cursor = connection.cursor()
        sql = '''CREATE TABLE myapp_othermodel (id INTEGER PRIMARY KEY);'''
        cursor.execute(sql)
        all_tables = set(connection.introspection.table_names())
        self.assertTrue('myapp_othermodel' in all_tables)
        # Run command with dry-run option. Nothing should have changed.
        result = self._call_command('site_cleanup', dry_run=True, verbosity=2)
        self.assertEqual(result[0], None)
        self.assertEqual(ContentType.objects.filter(app_label='myapp').count(), 1)
        all_tables = set(connection.introspection.table_names())
        self.assertTrue('myapp_othermodel' in all_tables)
        # Run command.  Extra content type and table should be gone.
        result = self._call_command('site_cleanup')
        self.assertEqual(result[0], None)
        self.assertEqual(ContentType.objects.filter(app_label='myapp').count(), 0)
        all_tables = set(connection.introspection.table_names())
        self.assertFalse('myapp_othermodel' in all_tables)
        # Change setting to refer to a nonexistent function, which should raise
        # an exception.
        settings.SITE_CLEANUP_FUNCTIONS = ['somepackage.somemodule.somefunction']
        result = self._call_command('site_cleanup')
        self.assertTrue(isinstance(result[0], Exception))
        # Change setting to our own function and verify it gets called.
        settings.SITE_CLEANUP_FUNCTIONS = ['test_project.test_app.tests.site_cleanup_function']
        result = self._call_command('site_cleanup')
        self.assertEqual(result[0], None)
        self.assertEqual(site_cleanup_function.has_been_called, True)

    def test_site_config(self):
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.com')
        self.assertEqual(site.domain, 'example.com')
        # With no options and verbosity=1, should display the current site.
        result = self._call_command('site_config', verbosity=1)
        self.assertEqual(result[0], None)
        self.assertTrue(site.name in result[1])
        self.assertTrue(site.domain in result[1])
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.com')
        self.assertEqual(site.domain, 'example.com')
        # Change only the name.
        result = self._call_command('site_config', _name='example.net')
        self.assertEqual(result[0], None)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.net')
        self.assertEqual(site.domain, 'example.com')
        # Change only the domain.
        result = self._call_command('site_config', domain='example.net')
        self.assertEqual(result[0], None)
        site = Site.objects.get_current()
        self.assertEqual(site.name, 'example.net')
        self.assertEqual(site.domain, 'example.net')
        # Change both name and domain.
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
        # Create superuser.
        super_user = User.objects.create_superuser('superfred', 'fred@ixmm.net', 'fredsPASS')
        super_user.first_name = 'Super'
        super_user.last_name = 'Fred'
        super_user.save()
        # Create inactive superuser.
        inactive_super_user = User.objects.create_superuser('deadfred', 'fred2@ixmm.net', 'fredsPASS')
        inactive_super_user.first_name = 'Dead'
        inactive_super_user.last_name = 'Fred'
        inactive_super_user.is_active = False
        inactive_super_user.save()
        # Create staff user.
        staff_user = User.objects.create_user('staffbob', 'bob@ixmm.net', 'bobsPASS')
        staff_user.first_name = 'Staff'
        staff_user.last_name = 'Bob'
        staff_user.is_staff = True
        staff_user.save()
        # Create staff user who is also in settings.MANAGERS.
        manager_staff_user = User.objects.create_user('david', 'david@ninemoreminutes.com', 'davesPASS')
        manager_staff_user.first_name = 'David'
        manager_staff_user.last_name = 'Horton'
        manager_staff_user.is_staff = True
        manager_staff_user.save()
        self.assertEqual(len(mail.outbox), 0)
        # Send to default recipients (admins).
        result = self._call_command('site_notify')
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[-1]
        expected_emails = set([x[1] for x in settings.ADMINS])
        for recipient in msg.to:
            realname, email_address = email.utils.parseaddr(recipient)
            self.assertTrue(email_address in expected_emails)
            expected_emails.remove(email_address)
        self.assertFalse(expected_emails)
        # Send to managers only.
        result = self._call_command('site_notify', managers=True)
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 2)
        msg = mail.outbox[-1]
        expected_emails = set([x[1] for x in settings.MANAGERS])
        for recipient in msg.to:
            realname, email_address = email.utils.parseaddr(recipient)
            self.assertTrue(email_address in expected_emails)
            expected_emails.remove(email_address)
        self.assertFalse(expected_emails)
        # Send to active superusers only.
        result = self._call_command('site_notify', superusers=True)
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 3)
        msg = mail.outbox[-1]
        users = User.objects.filter(is_active=True, is_superuser=True)
        expected_emails = set(users.values_list('email', flat=True))
        for recipient in msg.to:
            realname, email_address = email.utils.parseaddr(recipient)
            self.assertTrue(email_address in expected_emails)
            expected_emails.remove(email_address)
        self.assertFalse(expected_emails)
        # Send to active staff only.
        result = self._call_command('site_notify', staff=True)
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 4)
        msg = mail.outbox[-1]
        users = User.objects.filter(is_active=True, is_staff=True)
        expected_emails = set(users.values_list('email', flat=True))
        for recipient in msg.to:
            realname, email_address = email.utils.parseaddr(recipient)
            self.assertTrue(email_address in expected_emails)
            expected_emails.remove(email_address)
        self.assertFalse(expected_emails)
        # Send to managers and active staff. Email address in both lists should
        # only be listed once.
        result = self._call_command('site_notify', managers=True, staff=True)
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 5)
        msg = mail.outbox[-1]
        users = User.objects.filter(is_active=True, is_staff=True)
        expected_emails = set(users.values_list('email', flat=True))
        expected_emails.update([x[1] for x in settings.MANAGERS])
        for recipient in msg.to:
            realname, email_address = email.utils.parseaddr(recipient)
            self.assertTrue(email_address in expected_emails)
            expected_emails.remove(email_address)
        self.assertFalse(expected_emails)
        # Send to all admins, managers and staff.
        result = self._call_command('site_notify', all=True)
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 6)
        msg = mail.outbox[-1]
        users = User.objects.filter(is_active=True, is_staff=True)
        expected_emails = set(users.values_list('email', flat=True))
        users = User.objects.filter(is_active=True, is_superuser=True)
        expected_emails.update(users.values_list('email', flat=True))
        expected_emails.update([x[1] for x in settings.MANAGERS])
        expected_emails.update([x[1] for x in settings.ADMINS])
        for recipient in msg.to:
            realname, email_address = email.utils.parseaddr(recipient)
            self.assertTrue(email_address in expected_emails)
            expected_emails.remove(email_address)
        self.assertFalse(expected_emails)
        # Send to default recipients (admins) bcc'ed.
        result = self._call_command('site_notify', bcc=True)
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 7)
        msg = mail.outbox[-1]
        expected_emails = set([x[1] for x in settings.ADMINS])
        self.assertFalse(msg.to)
        for recipient in msg.bcc:
            realname, email_address = email.utils.parseaddr(recipient)
            self.assertTrue(email_address in expected_emails)
            expected_emails.remove(email_address)
        self.assertFalse(expected_emails)
        # Change default recipients via setting.
        settings.SITE_NOTIFY_DEFAULT_RECIPIENTS = ('admins', 'managers')
        result = self._call_command('site_notify')
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 8)
        msg = mail.outbox[-1]
        expected_emails = set([x[1] for x in settings.ADMINS])
        expected_emails.update([x[1] for x in settings.MANAGERS])
        for recipient in msg.to:
            realname, email_address = email.utils.parseaddr(recipient)
            self.assertTrue(email_address in expected_emails)
            expected_emails.remove(email_address)
        self.assertFalse(expected_emails)
        # Positional arguments should become message subject, then body.
        result = self._call_command('site_notify', 'test_subject', 'test_body', 'test_body2')
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 9)
        msg = mail.outbox[-1]
        self.assertTrue('test_subject' in msg.subject)
        self.assertTrue('test_body' in msg.body)
        self.assertTrue('test_body2' in msg.body)
        # Override subject and body templates via command line arguments.
        result = self._call_command('site_notify', subject_template='new_site_notify_subject.txt', body_template='new_site_notify_body.txt')
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 10)
        msg = mail.outbox[-1]
        self.assertTrue('NEW_SUBJECT' in msg.subject)
        self.assertTrue('NEW_BODY_SUFFIX' in msg.body)
        # Override subject and body templates via settings.
        settings.SITE_NOTIFY_SUBJECT_TEMPLATE = 'new_site_notify_subject.txt'
        settings.SITE_NOTIFY_BODY_TEMPLATE = 'new_site_notify_body.txt'
        result = self._call_command('site_notify')
        self.assertEqual(result[0], None)
        self.assertEqual(len(mail.outbox), 11)
        msg = mail.outbox[-1]
        self.assertTrue('NEW_SUBJECT' in msg.subject)
        self.assertTrue('NEW_BODY_SUFFIX' in msg.body)

    def _get_command_class(self, name):
        app_name = get_commands()[name]
        if isinstance(app_name, BaseCommand):
            instance = app_name
        else:
            instance = load_command_class(app_name, name)
        return type(instance)

    def _track_command_class(self, name):
        klass = self._get_command_class(name)
        klass.execute = trackcalls(klass.execute)
        self.assertFalse(klass.execute.has_been_called)

    def assertCommandCalled(self, name):
        klass = self._get_command_class(name)
        self.assertTrue(getattr(klass.execute, 'has_been_called', None))

    def assertCommandNotCalled(self, name):
        klass = self._get_command_class(name)
        self.assertFalse(getattr(klass.execute, 'has_been_called', None))

    def test_site_update(self):
        # Run site update with built-in default options, verify only expected
        # commands have been called.
        self._track_command_class('validate')
        self._track_command_class('syncdb')
        self._track_command_class('migrate')
        self._track_command_class('collectstatic')
        self._track_command_class('cleanup')
        result = self._call_command('site_update', interactive=False)
        self.assertEqual(result[0], None)
        self.assertCommandNotCalled('validate')
        self.assertCommandCalled('syncdb')
        self.assertCommandCalled('migrate')
        self.assertCommandCalled('collectstatic')
        self.assertCommandNotCalled('cleanup')
        # Replace the default update commands via settings.
        settings.SITE_UPDATE_COMMANDS = {
            'default': [
                'validate',
                'syncdb',
                'migrate',
                ('collectstatic', (), {'clear': True}),
            ],
            'clean': [
                'cleanup',
            ],
            'blah': [
                ('blah', (), {}, 'blahapp'),
            ],
            'argh': [
                'argh',
            ],
            'wtf': [
                (),
            ],
            'wtf2': [
                None,
            ],
        }
        # Run again and verify that the updated list of 'default' commands was
        # used.
        self._track_command_class('validate')
        self._track_command_class('syncdb')
        self._track_command_class('migrate')
        self._track_command_class('collectstatic')
        self._track_command_class('cleanup')
        result = self._call_command('site_update', interactive=False)
        self.assertEqual(result[0], None)
        self.assertCommandCalled('validate')
        self.assertCommandCalled('syncdb')
        self.assertCommandCalled('migrate')
        self.assertCommandCalled('collectstatic')
        self.assertCommandNotCalled('cleanup')
        # Run again using 'clean' subcommand, verify only the expected command
        # was called.
        self._track_command_class('validate')
        self._track_command_class('syncdb')
        self._track_command_class('migrate')
        self._track_command_class('collectstatic')
        self._track_command_class('cleanup')
        result = self._call_command('site_update', 'clean', interactive=False)
        self.assertEqual(result[0], None)
        self.assertCommandNotCalled('validate')
        self.assertCommandNotCalled('syncdb')
        self.assertCommandNotCalled('migrate')
        self.assertCommandNotCalled('collectstatic')
        self.assertCommandCalled('cleanup')
        # Run again using 'default' and 'clean' subcommands, verify that all
        # commands were called.
        self._track_command_class('validate')
        self._track_command_class('syncdb')
        self._track_command_class('migrate')
        self._track_command_class('collectstatic')
        self._track_command_class('cleanup')
        result = self._call_command('site_update', 'default', 'clean', interactive=False)
        self.assertEqual(result[0], None)
        self.assertCommandCalled('validate')
        self.assertCommandCalled('syncdb')
        self.assertCommandCalled('migrate')
        self.assertCommandCalled('collectstatic')
        self.assertCommandCalled('cleanup')
        # Run again using 'blah' subcommand, should still succeed since
        # 'blahapp' is specified and not installed.
        self._track_command_class('validate')
        self._track_command_class('syncdb')
        self._track_command_class('migrate')
        self._track_command_class('collectstatic')
        self._track_command_class('cleanup')
        result = self._call_command('site_update', 'blah', interactive=False)
        self.assertEqual(result[0], None)
        self.assertCommandNotCalled('validate')
        self.assertCommandNotCalled('syncdb')
        self.assertCommandNotCalled('migrate')
        self.assertCommandNotCalled('collectstatic')
        self.assertCommandNotCalled('cleanup')
        # Run again using 'argh' subcommand, should fail since 'argh' is an
        # unknown command.
        self._track_command_class('validate')
        self._track_command_class('syncdb')
        self._track_command_class('migrate')
        self._track_command_class('collectstatic')
        self._track_command_class('cleanup')
        result = self._call_command('site_update', 'argh', interactive=False)
        self.assertTrue(isinstance(result[0], SystemExit))
        self.assertCommandNotCalled('validate')
        self.assertCommandNotCalled('syncdb')
        self.assertCommandNotCalled('migrate')
        self.assertCommandNotCalled('collectstatic')
        self.assertCommandNotCalled('cleanup')
        # Run again using 'wtf' subcommand with invalid commands, should fail.
        result = self._call_command('site_update', 'wtf', interactive=False)
        self.assertTrue(isinstance(result[0], SystemExit))
        # Run again using 'wtf2' subcommand with invalid commands, should fail.
        result = self._call_command('site_update', 'wtf2', interactive=False)
        self.assertTrue(isinstance(result[0], SystemExit))
        # Run again using unknown subcommand, should fail.
        result = self._call_command('site_update', 'hoohah', interactive=False)
        self.assertTrue(isinstance(result[0], SystemExit))
