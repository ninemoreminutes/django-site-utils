# Python
from __future__ import unicode_literals

# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SiteUtilsConfig(AppConfig):

    name = 'site_utils'
    verbose_name = _('Site Utilities')
