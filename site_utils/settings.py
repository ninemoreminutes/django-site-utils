# Python
from __future__ import unicode_literals

# Django
from django.conf import settings

# Django-Site-Utils
from . import defaults


def get_site_utils_setting(name, merge_dicts=False):
    name = name.upper()
    try:
        default_setting = getattr(defaults, name)
        setting = getattr(settings, name, None)
        if merge_dicts:
            setting_dict = dict(default_setting.items())
            if setting:
                setting_dict.update(setting.items())
            return setting_dict
        else:
            return setting or default_setting
    except AttributeError:
        raise RuntimeError('invalid setting name: {}'.format(name))
