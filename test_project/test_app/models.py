# Django
from django.db import models

class Document(models.Model):
    """Test model with a file field."""

    title = models.CharField(max_length=100)
    doc = models.FileField(upload_to='documents')
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', related_name='documents',
                                   blank=True, null=True, default=None)

class Photo(models.Model):
    """Test model with an image field."""

    caption = models.CharField(max_length=100)
    image = models.ImageField(upload_to='photos')
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', related_name='photos',
                                   blank=True, null=True, default=None)
