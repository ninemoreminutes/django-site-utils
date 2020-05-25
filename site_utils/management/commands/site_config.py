# Python
from __future__ import unicode_literals
import json
from collections import OrderedDict

# Django
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

# Django-Site-Utils
from ...utils import app_is_installed


class Command(BaseCommand):

    help = 'View or modify the current/selected Site.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-n',
            '--name',
            action='store',
            dest='name',
            default=None,
            help='Update the site name.',
        )
        parser.add_argument(
            '-d',
            '--domain',
            action='store',
            dest='domain',
            default=None,
            help='Update the site domain.',
        )
        parser.add_argument(
            '--id',
            action='store',
            dest='site_id',
            type=int,
            default=0,
            help='Specify an alternate site ID to view/modify.',
        )
        parser.add_argument(
            '--create',
            action='store_true',
            dest='create',
            default=False,
            help='Create a new site if needed.',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all_sites',
            default=False,
            help='View/modify all sites.',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            dest='output_json',
            default=False,
            help='Output site details as JSON.',
        )

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        name = options.get('name', None) or options.get('_name', None)
        domain = options.get('domain', None)
        site_id = options.get('site_id', None)
        create = options.get('create', False)
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
            if create:
                create_kwargs = dict(id=site_id, name=name, domain=domain)
                create_kwargs = dict((k, v) for k, v in create_kwargs if v is not None)
                sites = [Site.objects.create(**create_kwargs)]
                if verbosity >= 2:
                    self.stderr.write('Created site: {}'.format(sites[0]))
            elif site_id:
                raise CommandError('Site with id={} not found'.format(site_id))
            else:
                raise CommandError('Current site not found')
        sites_data = []
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
                if verbosity >= 2:
                    self.stderr.write('Updated site: {} ({})'.format(site, ' & '.join(update_fields)))
            site_data = OrderedDict([
                ('id', site.pk),
                ('name', site.name),
                ('domain', site.domain),
            ])
            sites_data.append(site_data)
        if output_json:
            if all_sites:
                self.stdout.write('{}\n'.format(json.dumps(sites_data, indent=4)))
            else:
                self.stdout.write('{}\n'.format(json.dumps(sites_data[0], indent=4)))
        elif verbosity >= 1:
            for site_data in sites_data:
                self.stdout.write('ID={id} Name="{name}" Domain="{domain}"\n'.format(**site_data))
