# Python
from __future__ import unicode_literals

# Django
from django.db import models

# Django-Polymorphic
from polymorphic.models import PolymorphicModel


class Content(PolymorphicModel):

    # Separate date/time fields so we have those types for testing site_dump.
    created_date = models.DateField(
        auto_now_add=True,
    )
    created_time = models.TimeField(
        auto_now_add=True,
    )
    created_by = models.ForeignKey(
        'auth.User',
        related_name='content',
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        blank=True,
    )
    modified = models.DateTimeField(
        auto_now=True,
    )


class Document(Content):
    """Test model with a file field."""

    title = models.CharField(
        max_length=100,
    )
    doc = models.FileField(
        upload_to='documents',
    )


class Photo(Content):
    """Test model with an image field."""

    caption = models.CharField(
        max_length=100,
    )
    image = models.ImageField(
        upload_to='photos',
    )
