# Python
from __future__ import unicode_literals

# Django
from django.apps import AppConfig
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _


class SiteUtilsConfig(AppConfig):

    name = 'site_utils'
    verbose_name = _('Site Utilities')

    def ready(self):
        from .settings import get_site_utils_setting
        site_patch_functions = []
        for func_import in get_site_utils_setting('SITE_PATCHES'):
            site_patch_functions.append(import_string(func_import))
        for func in site_patch_functions:
            func()
