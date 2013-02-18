# Django
from django.contrib import admin

# Test App
from models import Document, Photo

admin.site.register(Document)
admin.site.register(Photo)
