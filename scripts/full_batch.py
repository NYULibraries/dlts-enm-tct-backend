import os
import shutil

from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

from otcore.lex.processing import read_stopwords
from otcore.management.manage_utils import erase_data
from otcore.relation.models import RelationType
from otcore.relation.processing import global_containment
from otx_epub.models import Epub
from otx_epub.extractors import EpubExtractor
from manuscripts.extractors import IndexExtractor
from manuscripts.cleaning import full_clean
from manuscripts.models import Index
from manuscripts.processing import nyu_global_multiple_tokens

OS_FILES = ['.DS_Store',]

    
def clear_epub_folder():
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


def run():
    """
    A Script to empty the database and do a full load and processing
    of the epub set
    """

    # Erase existing data
    erase_data()
    Epub.objects.all().delete()
    Index.objects.all().delete()

    # Clear out the decompressed folder
    if os.path.exists(settings.EPUB_DECOMPRESSED_FOLDER):
        clear_epub_folder()
    else:
        os.makedirs(settings.EPUB_DECOMPRESSED_FOLDER)

    # Load predefined indexpatterns
    call_command('loaddata', 'indexpatterns')

    # Create Project-Specific Relationtypes 
    RelationType.objects.get_or_create(
            rtype='See', role_from='See (Origin)', 
            role_to='See (Destination)', symmetrical=False)
    RelationType.objects.get_or_create(rtype='See Also', role_from='See Also (Origin)', role_to='See Also (Destination)', symmetrical=False)
    RelationType.objects.get_or_create(rtype='Subentry', role_from='Main Entry of', role_to='Subentry of', symmetrical=False)
    RelationType.objects.get_or_create(rtype='Generic')

    # Load lex parsing
    read_stopwords()

    # Load the epubs into extractors
    for root, subdirs, files in os.walk(settings.EPUB_SOURCES_FOLDER):
        for f in files:
            if f not in OS_FILES:
                filepath = os.path.join(root, f)

                extractor = EpubExtractor(filepath)
                extractor.extract_all()

                epub = extractor.document
                print("Extracting content and hits: {}".format(epub.title))
                IndexExtractor.extract_from_source(epub)

    # Hit cleaning
    full_clean()

    # Run automatic rules
    global_containment()
    nyu_global_multiple_tokens()
