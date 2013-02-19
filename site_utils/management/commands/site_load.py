# Django
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

class Command(BaseCommand):
    """Load the contents of a site from a site_dump backup."""

    @transaction.commit_on_success
    def handle(self, *args, **options):
        raise NotImplementedError # FIXME
