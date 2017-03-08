import zipfile
import os

from django.conf import settings

from otcore.occurrence.loaders import BaseLoader


class EpubFileLoader(BaseLoader):
    """
    Because an epub is essentially a structure zip file,
    It needs to be decompressed before being handed to the 
    Extractor. Actually parsing the Epub folder is handled by the
    EpubExtractor.
    """
    def load_source(self, source):
        epub_path = settings.EPUB_UPLOAD_FOLDER
        if epub_path in source:
            relative_path = source[len(epub_path):]
        else:
            relative_path = os.path.basename(source)

        if relative_path[0] == '/':
            relative_path = relative_path[1:]

        destination = os.path.join(settings.EPUB_DECOMPRESSED_FOLDER, relative_path)
        destination = destination[:len(destination)-5] # remove .epub extensions

        with zipfile.ZipFile(source, 'r', allowZip64=True) as zf:
            zf.extractall(destination)

        return destination
