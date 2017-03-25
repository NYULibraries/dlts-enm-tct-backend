import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from otx_epub.extractors import EpubExtractor

OS_FILES = ['.DS_Store',]


class Command(BaseCommand):
    help = 'Decompresses a .epub file and creates an Epub object. Pass the filename as an argument'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1)

    def handle(self, *args, **options):
        epub = None
        filename = options['filename'][0]

        for root, subdirs, files in os.walk(settings.EPUB_SOURCES_FOLDER):
            for f in files:
                if f not in OS_FILES:
                    if f == filename:
                        filepath = os.path.join(root, f)

                        extractor = EpubExtractor(filepath)
                        extractor.extract_all()

                        epub = extractor.document
                        break

        if epub is not None:
            self.stdout.write(self.style.SUCCESS('{} has been successfully added'.format(filename)))
        else:
            raise CommandError('Epub {} was not found'.format(filename))

