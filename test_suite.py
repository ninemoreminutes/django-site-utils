# Python
import os

# django-setuptest
import setuptest

class TestSuite(setuptest.setuptest.SetupTestSuite):

    def __init__(self, *args, **kwargs):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()
        super(TestSuite, self).__init__(*args, **kwargs)

    def resolve_packages(self):
        packages = super(TestSuite, self).resolve_packages()
        if 'test_app' not in packages:
            packages.append('test_app')
        return packages
