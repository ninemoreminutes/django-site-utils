# Python
from optparse import make_option

# Django
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

class Command(BaseCommand):
    """View/modify the current Site instance in the database."""

    option_list = BaseCommand.option_list + (
        make_option('-n', '--name', action='store', dest='name',
            default=None, help=_('Update the current Site name.')),
        make_option('-d', '--domain', action='store', dest='domain',
            default=None, help=_('Update the Site domain.')),
    )
    help = _('View or modify the current Site in the database.')
    requires_model_validation = True

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        name = options.get('name', None) or options.get('_name', None)
        domain = options.get('domain', None)
        site = Site.objects.get_current()
        if name:
            site.name = name
        if domain:
            site.domain = domain
        if name or domain:
            site.save()
        if verbosity >= 1:
            print 'ID=%d Name="%s" Domain="%s"' % (site.pk, site.name, site.domain)
