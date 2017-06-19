# Python
import os

# Django
from django.core.management.base import BaseCommand, CommandError
from django.test import override_settings
from django.test.client import RequestFactory

# BeautifulSoup
try:
    import bs4
except ImportError:
    bs4 = None

# Django-Site-Utils
from site_utils.views import handle_error


class Command(BaseCommand):

    help = 'Generate static error pages.'

    def parse_arguments(self, parser):
        parser.add_argument('status', nargs='+', type=int,
                            help='HTTP status code(s) of error pages to generate.')
        parser.add_argument('--dest', default='.',
                            help='Destination directory for generated pages.')
        parser.add_argument('--prefix', default='',
                            help='Prefix for generated filenames.')
        parser.add_argument('--suffix', default='.html',
                            help='Suffix for generated filenames.')
        parser.add_argument('--url', default='/',
                            help='URL prefix to determine which template to use.')
        parser.add_argument('--no-clean-html', action='store_false', dest='clean_html', default=True,
                            help='Disable cleaning tags from the generated HTML.')
        # TODO: Add arguments to select which HTML tags to clean.

    def clean_error_html(self, html):
        bs = bs4.BeautifulSoup(html, 'lxml')
        # Remove script tags.
        for tag in bs.findAll('script'):
            tag.extract()
        # Remove comments except IE conditionals
        for tag in bs.findAll(text=lambda text: isinstance(text, bs4.Comment)):
            if '[if' not in tag.string:
                tag.extract()
        # Replace relative links.
        for tag in bs.findAll('a', attrs={'href': True}):
            if tag['href'].startswith('/'):
                tag['href'] = '#'
        return bs.prettify()

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))
        statuses = options.get('status')
        dest_path = os.path.abspath(options.get('dest', '.'))
        prefix = options.get('prefix', '')
        suffix = options.get('suffix', '.html')
        url = options.get('url', '/')
        clean_html = options.get('clean_html', True)
        if clean_html and not bs4:
            raise CommandError('BeautifulSoup4 is required to clean the generated HTML. Specify --no-clean-html to disable this feature.')
        for status in statuses:
            with override_settings(ALLOWED_HOSTS=['testserver']):
                request = RequestFactory().get(url)
                response = handle_error(request, status)
            html = response.content
            if clean_html:
                html = self.clean_error_html(html)
            dest_file = os.path.join(dest_path, '{}{}{}'.format(prefix, status, suffix))
            if os.path.exists(dest_file):
                old_html = open(dest_file, 'rb').read()
                if html == old_html:
                    if verbosity >= 2:
                        self.stdout.write('No change to {} error for {} in {}.\n'.format(status, url, dest_file))
                    continue
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            open(dest_file, 'wb').write(html)
            if verbosity >= 1:
                self.stdout.write('Rendered HTML for {} error for {} to {}.\n'.format(status, url, dest_file))
