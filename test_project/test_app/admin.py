# Python
from __future__ import unicode_literals

# Django
from django.contrib import admin

# Django-Site-Utils
from site_utils.admin import ModelAdmin

# Test App
from .models import Document, Photo


@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    pass


@admin.register(Photo)
class PhotoAdmin(ModelAdmin):
    pass
