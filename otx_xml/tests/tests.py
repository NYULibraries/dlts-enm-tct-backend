import os

from django.test import TestCase

from otcore.hit.models import Hit
from otcore.occurrence.models import Document, Location, Content, Occurrence
from ..extractors import XMLExtractor
from ..models import XMLPattern


class XMLExtractorTests(TestCase):
    def setUp(self):
        self.shared_pattern_kwargs = {
            'xpath_locations': '/document/content/artist',
            'xpath_content': 'string(description/text())',
            'xpath_content_header': 'string(name/text())',
            'xpath_location_localid': 'string(@id)',
            'xpath_topic': 'tag/text()'
        }
        
        self.default_pattern = XMLPattern.objects.create(
            xpath_title='string(/document/metadata/data[@id="title"]/text())',
            xpath_author='string(/document/metadata/data[@id="author"]/text())',
            **self.shared_pattern_kwargs
        )

    def test_default_settings(self):
        """
        Loads the document in tests/test_xml_1.xml

        Checks to make sure the Location, Content, Occurrences, and Hits/Baskets
        are all create properly using the default XML extractors and pattern
        """

        self.assertEqual(Document.objects.count(), 0)
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(Content.objects.count(), 0)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(dir_path, 'test_xml_1.xml')

        extractor = XMLExtractor(filename)
        extractor.extract_all()

        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(extractor.document.author, "Matt Nishi-Broach")
        self.assertEqual(extractor.document.title, "Artists I Love")
        
        self.assertEqual(Location.objects.count(), 3)
        self.assertEqual(Content.objects.count(), 3)
        self.assertEqual(Hit.objects.count(), 10)
        self.assertEqual(Occurrence.objects.count(), 13)

        location = Location.objects.get(sequence_number=0)
        self.assertEqual(location.localid, '1')
        self.assertEqual(location.content.content_descriptor, "Joseph Cornell")
        self.assertEqual(location.content.text, 'Surrealist sculptor and collagist.  Fantastic diarama artist')
        self.assertEqual(location.occurrences.count(), 4)

    def test_alternate_pattern_name(self):
        """
        Loads the document in tests/test_xml_2.xml, which has an alternate
        document structure to tests/test_xml_1.xml.  The default pattern object
        should fail to parse properly, but dynamically loading the proper pattern object
        should find the document author and title correctly
        """
        second_pattern = XMLPattern.objects.create(
            name="second pattern",
            xpath_title='string(/document/description/title/text())',
            xpath_author='string(/document/description/author/text())',
            **self.shared_pattern_kwargs
        )

        dir_path = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(dir_path, 'test_xml_2.xml')

        wrong_extractor = XMLExtractor(filename)
        wrong_extractor.extract_all()

        self.assertEqual(wrong_extractor.document.author, "")
        self.assertEqual(wrong_extractor.document.title, "")

        Document.objects.all().delete()
        Location.objects.all().delete()
        Content.objects.all().delete()

        correct_extractor = XMLExtractor(filename, pattern_name="second pattern")
        correct_extractor.extract_all()

        self.assertEqual(correct_extractor.document.author, "Matt Nishi-Broach")
        self.assertEqual(correct_extractor.document.title, "Artists I Loathe")
