# Django
import django.dispatch

__all__ = []

site_cleanup = django.dispatch.Signal(providing_args=[])

site_update = django.dispatch.Signal(providing_args=[])
