import os

from django.core.management.base import BaseCommand, CommandError
from otcore.relation.processing import global_containment
from otx_epub.models import Epub
from manuscripts.extractors import IndexExtractor
from manuscripts.processing import nyu_global_multiple_tokens
from mauscripts.cleaning import full_clean


class Command(BaseCommand):
    help = 'Extracts Locations and Topics from a decompressed EPUB'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1)

    def handle(self, *args, **options):
        filename = options['filename'][0]

        epubs = Epub.objects.all()
        
        try:
            epub = [epub for epub in epubs if os.path.basename(epub.source.path) == filename][0]
        except IndexError:
            raise CommandError('No Epub matches the filename {}'.format(filename))

        IndexExtractor.extract_from_source(epub)

        full_clean()

        # Run automatic rules
        global_containment()
        nyu_global_multiple_tokens()

        self.stdout.write(self.style.SUCCESS('{} has been successfully extracted'.format(filename)))
