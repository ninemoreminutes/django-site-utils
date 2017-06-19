# Python
import json
from collections import OrderedDict

# Django
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

# Django-Site-Utils
from site_utils.utils import app_is_installed


class Command(BaseCommand):

    help = 'View or modify the current/selected Site.'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--name', action='store', dest='name', default=None,
                            help='Update the site name.')
        parser.add_argument('-d', '--domain', action='store', dest='domain', default=None,
                            help='Update the site domain.')
        parser.add_argument('--id', action='store', dest='site_id', type=int, default=0,
                            help='Specify an alternate site ID to view/modify.')
        parser.add_argument('--all', action='store_true', dest='all_sites', default=False,
                            help='View/modify all sites.')
        parser.add_argument('--json', action='store_true', dest='output_json', default=False,
                            help='Output site details as JSON.')

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        name = options.get('name', None) or options.get('_name', None)
        domain = options.get('domain', None)
        site_id = options.get('site_id', None)
        all_sites = options.get('all_sites', False)
        output_json = options.get('output_json', False)
        if not app_is_installed('django.contrib.sites'):
            raise CommandError('Sites app is not installed')
        try:
            if all_sites:
                sites = Site.objects.order_by('pk')
            elif site_id:
                sites = [Site.objects.get(pk=site_id)]
            else:
                sites = [Site.objects.get_current()]
        except Site.DoesNotExist:
            if site_id:
                raise CommandError('Site with id={} not found'.format(site_id))
            else:
                raise CommandError('Current site not found')
        all_sites_data = []
        for site in sites:
            update_fields = []
            if name:
                site.name = name
                update_fields.append('name')
            if domain:
                site.domain = domain
                update_fields.append('domain')
            if update_fields:
                site.save(update_fields=update_fields)
            if output_json:
                site_data = OrderedDict([
                    ('id', site.pk),
                    ('name', site.name),
                    ('domain', site.domain),
                ])
                if all_sites:
                    all_sites_data.append(site_data)
                else:
                    self.stdout.write('{}\n'.format(json.dumps(site_data, indent=4)))
            elif verbosity >= 1:
                self.stdout.write('ID={} Name="{}" Domain="{}"\n'.format(site.pk, site.name, site.domain))
        if all_sites and output_json:
            self.stdout.write('{}\n'.format(json.dumps(all_sites_data, indent=4)))
