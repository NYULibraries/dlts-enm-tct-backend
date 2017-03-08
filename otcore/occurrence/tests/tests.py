from unittest import mock
import os

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from ..extractors import BaseDocumentExtractor
from ..models import Content, Location, Document
from ..loaders import FileLoader
from otcore.hit.models import Hit, Basket


class DummyExtractor(BaseDocumentExtractor):
    """
    Minimum viable dummy DocumentExtractor implementation
    """
    extract_hits = False

    def create_locations(self):
        """
        Creates a single dummy location and content pair.
        timezone.now() used for `content_unique_indicator` to prevent
        IntegrityErrors when performing bulk extraction
        """
        content = Content.objects.create(
                content_unique_indicator="Dummy Content {}".format(timezone.now()),
                content_descriptor = "Dummy Content",
                text = "Dummy content for fake testing location"
        )

        location = Location.objects.create(
                content=content,
                document=self.document,
                filepath="path/to/file"
        )

    def create_title(self):
        """
        Uses timezone.now() to create unique document titles
        """
        return "Dummy Title {}".format(timezone.now())


class BaseExtractorTests(TestCase):
    def test_no_source_error(self):
        """
        Ensure that not passing a source to the BaseDocumentExtractor
        raises an error
        """
        with self.assertRaises(TypeError):
            extractor = BaseDocumentExtractor()


    def test_no_document_exctractor(self):
        """
        Test that an implementation without `create_locations()`
        will raise a `NotImplementedError`
        """
        extractor = BaseDocumentExtractor("Dummy Source")
        with self.assertRaises(NotImplementedError):
            extractor.extract_all()

    def test_base_dummy_extractor(self):
        """
        Runs single extraction using the dummy extract.
        Ensure the properly number of and relationship between
        Documents, Contents, and Locations
        """
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(Content.objects.count(), 0)

        extractor = DummyExtractor("Dummy Source")
        extractor.extract_all()

        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Content.objects.count(), 1)
        self.assertEqual(Location.objects.all()[0].document,
                         Document.objects.all()[0])

    def test_base_dummy_extractor_class_method(self):
        """
        Same as above, but using the classmethod approach
        """
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(Content.objects.count(), 0)

        DummyExtractor.extract_from_source("Dummy Source")

        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(Content.objects.count(), 1)
        self.assertEqual(Location.objects.all()[0].document,
                         Document.objects.all()[0])

    def test_base_dummy_extractor_bulk(self):
        """
        Test bulk extraction using multiplate sources.
        Ensure the proper number of Documents, Locations, and Contents
        are created.
        """
        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(Content.objects.count(), 0)

        sources = ['First Dummy Source', 'Second Dummy Source', 'Another Dummy']
        DummyExtractor.bulk_extract(sources)

        self.assertEqual(Document.objects.count(), 3)
        self.assertEqual(Location.objects.count(), 3)
        self.assertEqual(Content.objects.count(), 3)

    def test_hits_not_implemented_error(self):
        """
        Ensures appropriate exception is raised if `extract_hits` is True
        and `create_hits()` is not overridden
        """
        extractor = DummyExtractor("Dummy Source", extract_hits=True)

        with self.assertRaises(NotImplementedError):
            extractor.extract_all()
