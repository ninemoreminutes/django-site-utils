# Python
import socket

# Django
from django.conf import settings as django_settings


def hostname(request):
    return {
        'hostname': socket.gethostname(),
    }


def settings(request):
    return {
        'settings': django_settings,
    }
