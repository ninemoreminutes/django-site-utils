# Python
from __future__ import unicode_literals
import re

# Django
from django.shortcuts import render
from django.template import Context
from django.template.context import RequestContext
from django.utils.translation import gettext_lazy as _

# Django-Site-Utils
from .settings import get_site_utils_setting


def handle_error(request, status, title=None, message=None, exception=None, template_name=None):
    error_messages = get_site_utils_setting('SITE_ERROR_MESSAGES', merge_dicts=True)
    if not template_name:
        error_templates = get_site_utils_setting('SITE_ERROR_TEMPLATES')
        template_name = 'site_utils/error.html'
        for regex, template in error_templates:
            if re.match(regex, request.path.lstrip('/')):
                template_name = template or template_name
                break
    if title is None:
        title = error_messages.get(status, (_('Unknown Error'),))[0]
    if message is None:
        message = error_messages.get(status, (None, _('An unknown error occurred')))[1]
    error_context = {
        'error_title': title,
        'error_message': message,
        'error_status': status,
        'exception': exception,
    }
    try:
        context = RequestContext(request, error_context)
    except Exception:
        raise  # FIXME: Which exception is raised?
        context = Context(error_context)
    response = render(request, template_name, context.flatten())
    response.status_code = status
    return response


def handle_400(request, exception=None, template_name=None):
    return handle_error(request, 400, exception=exception, template_name=template_name)


def handle_403(request, exception=None, template_name=None):
    return handle_error(request, 403, exception=exception, template_name=template_name)


def handle_404(request, exception=None, template_name=None):
    return handle_error(request, 404, exception=exception, template_name=template_name)


def handle_500(request, template_name=None):
    return handle_error(request, 500, template_name=template_name)
