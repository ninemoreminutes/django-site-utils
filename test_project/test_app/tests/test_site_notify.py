# Python
from __future__ import unicode_literals
import email.utils

# Django
import django


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
    if django.VERSION >= (2, 0):
        assert isinstance(result[0], Exception)
