# Python
from __future__ import unicode_literals

# Django
import django.dispatch

__all__ = ['site_update']

site_update = django.dispatch.Signal(providing_args=[])
