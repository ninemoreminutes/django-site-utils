# Python
from __future__ import unicode_literals

# Test App
from . import trackcalls


@trackcalls
def site_cleanup_function(**options):
    pass


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
    settings.SITE_CLEANUP_FUNCTIONS = ['test_project.test_app.tests.test_site_cleanup.site_cleanup_function']
    result = command_runner('site_cleanup')
    assert result[0] is None
    assert site_cleanup_function.has_been_called
