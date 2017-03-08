import os
import shutil

from django.test import TestCase
from django.conf import settings

from otcore.occurrence.models import Document
from ..models import Epub
from ..extractors import EpubExtractor


class EpubExtractorTests(TestCase):
    def clear_epub_folder(self):
        """
        Utility to empty the temp epub decompressed folder, to avoid file conflicts

        deletion code adapted from:
        http://stackoverflow.com/a/185941/3362468
        """
        folder = settings.EPUB_DECOMPRESSED_FOLDER

        for f in os.listdir(folder):
            filepath = os.path.join(folder, f)

            try:
                if os.path.isfile(filepath):
                    os.unlink(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
            except Exception as e:
                print(e)

    def test_default_epub_extractor(self):
        """
        Loads and parses the epub tests/owl_creek.epub, A copy of Ambrose Bierce's
        'An Occurrence at Owl Creek Bridge', courtesy of Project Guttenburg.

        It should create a decompressed version of the Epub in /tmp,
        and an Epub object with the correct fields
        """
        self.assertEqual(Epub.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 0)
        self.clear_epub_folder()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(dir_path, 'owl_creek.epub')

        extractor = EpubExtractor(filename)
        extractor.extract_all()

        self.assertEqual(Epub.objects.count(), 1)

        epub = extractor.document

        self.assertEqual(epub.title, 'An Occurrence at Owl Creek Bridge')
        self.assertEqual(epub.author, 'Ambrose Bierce')
        self.assertEqual(epub.publisher, '')
        self.assertEqual(os.path.basename(epub.manifest), 'content.opf')
        self.assertEqual(os.path.basename(epub.oebps_folder), 'OEBPS')
