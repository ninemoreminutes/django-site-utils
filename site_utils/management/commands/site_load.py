# Django
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

class Command(BaseCommand):
    """Load the contents of the entire site from a dumpsite backup."""

    @transaction.commit_on_success
    def handle(self, *args, **options):
        raise NotImplementedError # FIXME
