import os
from lxml import etree

from otcore.occurrence.loaders import FileLoader
from otcore.occurrence.extractors import BaseDocumentExtractor
from .models import Epub
from .loaders import EpubFileLoader



namespaces = {
    'container': "urn:oasis:names:tc:opendocument:xmlns:container",
    'dc': 'http://purl.org/dc/elements/1.1',
    'opf': 'http://www.idpf.org/2007/opf',
    'html': 'http://www.w3.org/1999/xhtml',
    'epub': 'http://www.idpf.org/2007/ops',
    'otl': 'http://www.infoloom.nyc/otl',
    'svg': "http://www.w3.org/2000/svg",
}

class EpubExtractor(BaseDocumentExtractor):
    """
    Generic class for loading and parsing Epub files into Epub files (a child class
    of otcore's Dcoument).  

    Note that because of the variety of Epub structures and possibile ways of parsing,
    the base implementation does not actually include extracting of locations, content,
    and topis from the Epub.  It is recommended that you combine this extractor with
    another, such as XMLExtractor, to create project-specific parsing

    lxml is required for parsing the metadata
    """

    default_loader = EpubFileLoader

    extract_hits = False
    extract_locations = False

    def import_document(self):
        """
        Should get the location of the decompressed epub folder from the loader
        """
        self.epub_folder = self.loader.load_source(self.source)

    def create_document(self):
        """
        Uses the Epub model instead of the Document model, to store
        Epub specific information
        """

        oebps_folder = self.get_oebps_folder()
        manifest = self.get_manifest()

        manifest_tree = etree.parse(manifest).getroot()

        title = self.extract_title(manifest_tree)
        author = self.extract_author(manifest_tree)
        publisher = self.extract_publisher(manifest_tree)

        epub, _ = Epub.objects.get_or_create(
            author=author, title=title, publisher=publisher,
            defaults = {
                'contents': self.epub_folder,
                'oebps_folder': oebps_folder,
                'manifest': manifest
            }
        )

        return epub

    def get_oebps_folder(self):
        oebps_folder = None
        for item in os.listdir(self.epub_folder):
            full_path = os.path.join(self.epub_folder, item)
            if os.path.isdir(full_path) and item.lower() != 'meta-inf':
                oebps_folder = full_path
                break

        if oebps_folder is None:
            raise FileNotFoundError(
                'Decompressed epub does not have an oebps folder. '
                'Please ensure the original file is a properly structured epub.'
            )

        return oebps_folder

    def get_manifest(self):
        """
        Parses the epub container file and finds the manifest
        """
        container = os.path.join(self.epub_folder, 'META-INF', 'container.xml')

        container_tree = etree.parse(container).getroot()

        rootfile = container_tree.xpath(
            '//container:rootfile/@full-path', 
            namespaces=namespaces)[0]

        manifest = os.path.join(self.epub_folder, rootfile)

        return manifest

    def extract_title(self, manifest_tree):
        return self.fetch_from_dc(manifest_tree, 'title')

    def extract_author(self, manifest_tree):
        return self.fetch_from_dc(manifest_tree, 'creator')

    def extract_publisher(self, manifest_tree):
        return self.fetch_from_dc(manifest_tree, 'publisher')

    def fetch_from_dc(self, manifest_tree, value):
        """
        Parses and returns a specific value from the manifest Dublin Core metafile
        manfifest_tree is the lxml parsed manifest file
        value is the Dublin Core key you want fetched

        will return the value of the key if its found, otherwise an empty string
        """
        node = manifest_tree.find('.//{{http://purl.org/dc/elements/1.1/}}{}'.format(value))
        
        text = node.text if node is not None else ''

        return text
