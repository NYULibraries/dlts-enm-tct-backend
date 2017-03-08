import logging

from .models import Document
from .loaders import BaseLoader


logger = logging.getLogger(__name__)


class BaseDocumentExtractor:
    """
    Generic Interface for running extraction on Documents.
    Creates a set of Documents, Locations, and Contents from a given input.
    Optionally creates hits/baskets if hit_extraction is set to True

    This is used as a base class for more specific Document types,
    including the other generics included here
    """
    extract_hits = True
    extract_locations = True
    extract_document = True

    default_loader = BaseLoader

    def __init__(self, source, loader=None, **kwargs):
        self.source = source
        self.loader = loader() if loader else self.default_loader()

        self.loader.validate_source(source)

        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def extract_from_source(cls, source, loader=None, **kwargs):
        """
        Shortcut for exctracting/parsing a single Document
        """
        extractor = cls(source, loader=loader, **kwargs)
        extractor.extract_all()

    @classmethod
    def bulk_extract(cls, sources, **kwargs):
        """
        Shortcut batch extraction.  Simply calls extract_from_source()
        using an iterable of sources
        """
        for source in sources:
            cls.extract_from_source(source, loader=None, **kwargs)

    def extract_all(self):
        """
        Wrapper function to extract all information from a given source
        """
        self.import_document()

        if self.extract_document:
            self.document = self.create_document()

        if self.extract_locations:
            self.locations = self.create_locations()

        if self.extract_hits:
            self.occurrences = self.create_hits()

        logger.info("Extracted all info from {}".format(self.source))

    def create_document(self):
        """
        Wrapper function for extracting all of the Document model fields.
        This way individual extraction methods can be overridden.
        By default, all of the fields are set to None
        """
        title = self.create_title()
        author = self.create_author()

        document, _ = Document.objects.get_or_create(
            title=title,
            author=author,
        )

        return document

    def create_title(self):
        """
        Function for populating the Document "title" field
        """
        return None

    def create_author(self):
        """
        Function for populating the Document "author" field
        """
        return None

    def create_locations(self):
        """
        Creates all locations and content for a given document.
        Must be instantiated by inherited class
        """
        msg = (
            "{} must override the `create_locations()` function"
            "to define how locations are extract from its given"
            "Document type"
            .format(self.__class__.__name__)
        )
        raise NotImplementedError(msg)

    def create_hits(self):
        """
        Creats hits/baskets and their associated occurrences.
        Only runs if `extract_hits` is True
        """
        msg = (
            "{} must either override the `create_hits()`"
            "function or set `extract_hits` to False"
            .format(self.__class__.__name__)
        )
        raise NotImplementedError(msg)

    def import_document(self):
        """
        Optional processing step for loading and parsing documents
        """
        pass
