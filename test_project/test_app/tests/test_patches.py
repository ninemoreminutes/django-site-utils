# Python
from __future__ import unicode_literals

# Site-Utils
import site_utils.patches


def test_patch_runserver_addrport(apps):
    assert site_utils.patches._runserver_addrport_patched.is_set()


def test_patch_wsgi_handler_keep_alive(apps):
    assert site_utils.patches._wsgi_handler_keep_alive_patched.is_set()
