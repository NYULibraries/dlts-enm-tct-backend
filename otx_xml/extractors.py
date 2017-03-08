from lxml import etree

from otcore.occurrence.extractors import BaseDocumentExtractor
from otcore.occurrence.loaders import FileLoader
from otcore.occurrence.models import Content, Location, Occurrence
from otcore.hit.models import Hit
from .models import XMLPattern


class XMLExtractor(BaseDocumentExtractor):
    """
    Generic Extractor for parsing a single xml document into Documents, Locations, Content, 
    and extracting topics.

    In order to be as reusable as possible, the extractor uses an extraction_pattern model
    to get the requiste xpath and metdata.  This defaults to usung the XMLPattern model from 
    this app, but that can be overwritten.

    lxml is used to load and parse the xml, which can be accessed afer loading in self.tree.
    Note that to standardize loading, the extractor is expecting the xml as a string, not
    as bytes
    """

    default_pattern_model = XMLPattern
    default_pattern_name = 'default'
    default_loader = FileLoader

    def __init__(self, source, loader=None, pattern_name=None, pattern_model=None, **kwargs):
        pattern_model = pattern_model or self.default_pattern_model
        pattern_name = pattern_name or self.default_pattern_name

        self.pattern = pattern_model.objects.get(name=pattern_name) 

        super(XMLExtractor, self).__init__(source, loader, **kwargs)

    def import_document(self):
        xml_string = self.loader.load_source(self.source)

        self.tree = etree.fromstring(xml_string)

    def extract_title(self):
        return self.tree.xpath(self.pattern.xpath_title)

    def extract_author(self):
        return self.tree.xpath(self.pattern.xpath_author)

    def create_locations(self):
        """
        Iterates through location nodes, and creates both Location and Content objects
        """
        nodes = self.tree.xpath(self.pattern.xpath_locations)
        seq_num = 0

        locations = []
        for node in nodes:
            content = self.create_content(node)

            if content:
                location = self.create_location(content, seq_num, node)

                # Store the location node in the location object, for referencing in future 
                # processing, if necessary
                location.node = node
                locations.append(location)
                seq_num += 1

        return locations

    def create_content(self, node):
        """
        Creates a content object from a given location node

        Uses the xpath_content_header to find the content_descriptor if it exists,
        otherwise it takes the first 50 characters of the text
        """
        text = node.xpath(self.pattern.xpath_content)

        if self.pattern.xpath_content_header:
            header = node.xpath(self.pattern.xpath_content_header)
        else:
            header = text[:50]

        content, _ = Content.objects.get_or_create(
            content_descriptor=header,
            defaults = {
                'text': text
            })

        return content

    def create_location(self, content, seq_num, node):
        """
        Given the Content objects, sequence number, and location node, 
        constructs the actual Location object for the given node
        """
        if self.pattern.xpath_location_localid:
            localid = node.xpath(self.pattern.xpath_location_localid)
        else:
            localid = content.content_descriptor

        location = Location.objects.create(
            sequence_number=seq_num, filepath=self.source,
            document=self.document, content=content,
            localid=localid
        )

        return location

    def create_hits(self):
        """
        Extracts topics from locations and creates corresponding Occurrences

        By default, it looks for hits in a given location node using the pattern.xpath_topic
        string
        """

        occurrences = []

        for location in self.locations:
            names = location.node.xpath(self.pattern.xpath_topic)

            for name in names:
                hit, _ = Hit.objects.get_or_create(name=name)
                hit.create_basket_if_needed()

                basket = hit.basket

                occurrence = Occurrence.objects.create(
                    location=location,
                    basket=basket
                )

                occurrences.append(occurrence)

        return occurrences
