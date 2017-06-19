# Django
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404


def bad_request(request):
    raise SuspiciousOperation


def forbidden(request):
    raise PermissionDenied


def not_found(request):
    raise Http404


def server_error(request):
    raise RuntimeError
