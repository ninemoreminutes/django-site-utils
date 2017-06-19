# Python
import datetime
import email.utils
import functools
import hashlib
import os
import shutil
import sys
import StringIO
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
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group, Permission
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.sites.models import Site
from django.db import connection, models
from django.utils.encoding import is_protected_type

# Django-Site-Utils
from site_utils import defaults
from site_utils.serializers import SiteJsonEncoder
from site_utils.utils import app_is_installed

# Test App
from models import Document, Photo

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
        settings.MEDIA_ROOT = tempfile.mkdtemp()
        self._temp_dirs = [settings.MEDIA_ROOT]
        self._cwd = os.getcwd()

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
        for temp_dir in self._temp_dirs:
            shutil.rmtree(temp_dir, True)
        os.chdir(self._cwd)

    def _call_command(self, name, *args, **options):
        options.setdefault('verbosity', 0)
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = StringIO.StringIO()
        sys.stderr = StringIO.StringIO()
        result = None
        try:
            #exc_info = None
            result = call_command(name, *args, **options)
        except Exception, e:
            #exc_info = sys.exc_info()
            result = e
        except SystemExit, e:
            #exc_info = sys.exc_info()
            result = e
        finally:
            captured_stdout = sys.stdout.getvalue()
            captured_stderr = sys.stderr.getvalue()
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        #if exc_info:
        #    sys.excepthook(*exc_info)
        return result, captured_stdout, captured_stderr


def test_app_is_installed():
    assert app_is_installed('contenttypes')
    assert app_is_installed('django.contrib.contenttypes')
    assert app_is_installed('admin')
    assert app_is_installed('django.contrib.admin')
    assert not app_is_installed('flatpages')
    assert not app_is_installed('django.contrib.flatpages')
    assert app_is_installed('site_utils')


@pytest.mark.parametrize('status_code,view_name', [
    (400, 'bad-request'),
    (403, 'forbidden'),
    (404, 'not-found'),
    (500, 'server-error'),
])
def test_error_views(client, status_code, view_name, settings):
    # Test normal error views for main site.
    url = reverse('error-views:{}'.format(view_name))
    response = client.get(url)
    assert response.status_code == status_code
    template_names = [t.name for t in response.templates if t.name is not None]
    assert 'site_utils/error.html' in template_names, response.content

    # Test alternate error views for admin site.
    url = reverse('admin-error-views:{}'.format(view_name))
    response = client.get(url)
    assert response.status_code == status_code
    template_names = [t.name for t in response.templates if t.name is not None]
    assert 'admin/error.html' in template_names


def test_site_cleanup(content_type_model, db_connection, command_runner, settings):
    # Create dummy content type.
    assert not content_type_model.objects.filter(app_label='myapp').exists()
    content_type_model.objects.create(app_label='myapp', model='mymodel')
    assert content_type_model.objects.filter(app_label='myapp').exists()

    # Create extra database table.
    all_tables = set(db_connection.introspection.table_names())
    assert 'myapp_othermodel' not in all_tables
    cursor = db_connection.cursor()
    sql = '''CREATE TABLE myapp_othermodel (id INTEGER PRIMARY KEY);'''
    cursor.execute(sql)
    all_tables = set(db_connection.introspection.table_names())
    assert 'myapp_othermodel' in all_tables

    # Run command with dry-run option. Nothing should have changed.
    result = command_runner('site_cleanup', dry_run=True, verbosity=2)
    assert result[0] is None
    assert content_type_model.objects.filter(app_label='myapp').exists()
    all_tables = set(db_connection.introspection.table_names())
    assert 'myapp_othermodel' in all_tables

    # Run command.  Extra content type and table should be gone.
    result = command_runner('site_cleanup')
    assert result[0] is None
    assert not content_type_model.objects.filter(app_label='myapp').exists()
    all_tables = set(db_connection.introspection.table_names())
    assert 'myapp_othermodel' not in all_tables

    # Change setting to refer to a nonexistent function, which should raise an exception.
    settings.SITE_CLEANUP_FUNCTIONS = ['somepackage.somemodule.somefunction']
    result = command_runner('site_cleanup')
    assert isinstance(result[0], Exception)

    # Change setting to our own function and verify it gets called.
    settings.SITE_CLEANUP_FUNCTIONS = ['test_project.test_app.tests.site_cleanup_function']
    result = command_runner('site_cleanup')
    assert result[0] is None
    assert site_cleanup_function.has_been_called


def test_site_config(site_model, command_runner, settings):
    # Get current site.
    site = site_model.objects.get_current()
    assert site.name == 'example.com'
    assert site.domain == 'example.com'

    # With no options and verbosity=1, should display the current site.
    result = command_runner('site_config', verbosity=1)
    assert result[0] is None
    assert 'Name="{}"'.format(site.name) in result[1]
    assert 'Domain="{}"'.format(site.domain) in result[1]
    site.refresh_from_db()
    assert site.name == 'example.com'
    assert site.domain == 'example.com'

    # Change only the name.
    result = command_runner('site_config', _name='example net site')
    assert result[0] is None
    site.refresh_from_db()
    assert site.name == 'example net site'
    assert site.domain == 'example.com'

    # Change only the domain.
    result = command_runner('site_config', domain='example.net')
    assert result[0] is None
    site.refresh_from_db()
    assert site.name == 'example net site'
    assert site.domain == 'example.net'

    # Change both name and domain.
    result = command_runner('site_config', _name='example org site', domain='example.org')
    assert result[0] is None
    site.refresh_from_db()
    assert site.name == 'example org site'
    assert site.domain == 'example.org'

    # Remove django.contrib.sites and try to run the command.
    settings.INSTALLED_APPS = (x for x in settings.INSTALLED_APPS if x != 'django.contrib.sites')
    result = command_runner('site_config')
    assert isinstance(result[0], Exception)


def test_site_notify_default(command_runner, mailoutbox, settings):
    # Send to default recipients (admins).
    assert settings.ADMINS
    result = command_runner('site_notify')
    assert result[0] is None
    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    expected_emails = set([x[1] for x in settings.ADMINS])
    for recipient in msg.to:
        realname, email_address = email.utils.parseaddr(recipient)
        assert email_address in expected_emails
        expected_emails.remove(email_address)
    assert not expected_emails


def test_site_notify_managers(command_runner, mailoutbox, settings):
    # Send to addresses listed in settings.MANAGERS.
    assert settings.MANAGERS
    result = command_runner('site_notify', managers=True)
    assert result[0] is None
    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    expected_emails = set([x[1] for x in settings.MANAGERS])
    for recipient in msg.to:
        realname, email_address = email.utils.parseaddr(recipient)
        assert email_address in expected_emails
        expected_emails.remove(email_address)
    assert not expected_emails


def test_site_notify_superusers(user_model, super_user, inactive_super_user,
                                command_runner, mailoutbox):
    # Send to active superusers.
    result = command_runner('site_notify', superusers=True)
    assert result[0] is None
    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    users = user_model.objects.filter(is_active=True, is_superuser=True)
    expected_emails = set(users.values_list('email', flat=True))
    for recipient in msg.to:
        realname, email_address = email.utils.parseaddr(recipient)
        assert email_address in expected_emails
        expected_emails.remove(email_address)
    assert not expected_emails


def test_site_notify_staff(user_model, super_user, inactive_super_user,
                           staff_user, manager_staff_user, command_runner,
                           mailoutbox):
    # Send to active staff users.
    result = command_runner('site_notify', staff=True)
    assert result[0] is None
    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    users = user_model.objects.filter(is_active=True, is_staff=True)
    expected_emails = set(users.values_list('email', flat=True))
    for recipient in msg.to:
        realname, email_address = email.utils.parseaddr(recipient)
        assert email_address in expected_emails
        expected_emails.remove(email_address)
    assert not expected_emails


def test_site_notify_managers_staff(user_model, super_user, inactive_super_user,
                                    staff_user, manager_staff_user,
                                    command_runner, mailoutbox, settings):
    # Send to managers and active staff. Email address in both lists should
    # only be listed once.
    result = command_runner('site_notify', managers=True, staff=True)
    assert result[0] is None
    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    users = user_model.objects.filter(is_active=True, is_staff=True)
    expected_emails = set(users.values_list('email', flat=True))
    expected_emails.update([x[1] for x in settings.MANAGERS])
    for recipient in msg.to:
        realname, email_address = email.utils.parseaddr(recipient)
        assert email_address in expected_emails
        expected_emails.remove(email_address)
    assert not expected_emails


def test_site_notify_all(user_model, super_user, inactive_super_user,
                         staff_user, manager_staff_user, command_runner,
                         mailoutbox, settings):
    # Send to all admins, managers and staff.
    result = command_runner('site_notify', all_users=True)
    assert result[0] is None
    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    users = user_model.objects.filter(is_active=True, is_staff=True)
    expected_emails = set(users.values_list('email', flat=True))
    users = user_model.objects.filter(is_active=True, is_superuser=True)
    expected_emails.update(users.values_list('email', flat=True))
    expected_emails.update([x[1] for x in settings.MANAGERS])
    expected_emails.update([x[1] for x in settings.ADMINS])
    for recipient in msg.to:
        realname, email_address = email.utils.parseaddr(recipient)
        assert email_address in expected_emails
        expected_emails.remove(email_address)
    assert not expected_emails


def test_site_notify_bcc(command_runner, mailoutbox, settings):
    # Send to default recipients (admins) bcc'ed.
    result = command_runner('site_notify', bcc=True)
    assert result[0] is None
    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    expected_emails = set([x[1] for x in settings.ADMINS])
    assert not msg.to
    for recipient in msg.bcc:
        realname, email_address = email.utils.parseaddr(recipient)
        assert email_address in expected_emails
        expected_emails.remove(email_address)
    assert not expected_emails


def test_site_notify_change_default(command_runner, mailoutbox, settings):
    # Change default recipients via setting.
    assert settings.ADMINS
    assert settings.MANAGERS
    settings.SITE_NOTIFY_DEFAULT_RECIPIENTS = ('admins', 'managers')
    result = command_runner('site_notify')
    assert result[0] is None
    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    expected_emails = set([x[1] for x in settings.ADMINS])
    expected_emails.update([x[1] for x in settings.MANAGERS])
    for recipient in msg.to:
        realname, email_address = email.utils.parseaddr(recipient)
        assert email_address in expected_emails
        expected_emails.remove(email_address)
    assert not expected_emails


def test_site_notify_subject_body(command_runner, mailoutbox):
    # Positional arguments should become message subject, then body.
    result = command_runner('site_notify', 'test_subject', 'test_body', 'test_body2')
    assert result[0] is None
    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    assert 'test_subject' in msg.subject
    assert 'test_body' in msg.body
    assert 'test_body2' in msg.body


def test_site_notify_templates(command_runner, mailoutbox):
    # Override subject and body templates via command line arguments.
    result = command_runner('site_notify',
                            subject_template='new_site_notify_subject.txt',
                            body_template='new_site_notify_body.txt')
    assert result[0] is None
    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    assert 'NEW_SUBJECT' in msg.subject
    assert 'NEW_BODY_SUFFIX' in msg.body

    
def test_site_notify_template_settings(command_runner, mailoutbox, settings):
    # Override subject and body templates via settings.
    settings.SITE_NOTIFY_SUBJECT_TEMPLATE = 'new_site_notify_subject.txt'
    settings.SITE_NOTIFY_BODY_TEMPLATE = 'new_site_notify_body.txt'
    result = command_runner('site_notify')
    assert result[0] is None
    assert len(mailoutbox) == 1
    msg = mailoutbox[0]
    assert 'NEW_SUBJECT' in msg.subject
    assert 'NEW_BODY_SUFFIX' in msg.body


def test_site_notify_auth_not_installed(command_runner, mailoutbox, settings):
    # Send to default recipients (admins).
    settings.INSTALLED_APPS = (x for x in settings.INSTALLED_APPS if x != 'django.contrib.auth')
    result = command_runner('site_notify')
    assert result[0] is None
    result = command_runner('site_notify', superusers=True)
    assert result[0] is None


class Foo:
    


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

    def test_site_load(self):
        output = self.test_site_dump()
        result = self._call_command('site_load', output)
        self.assertEqual(result[0], None)

        raise NotImplementedError

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
