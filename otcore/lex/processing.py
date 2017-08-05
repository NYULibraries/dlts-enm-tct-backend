import importlib
from otcore.settings import otcore_settings
import codecs

from .models import StopWord, Recognizer


def lines_in_file(filename):
    """
    returns a list, each item is a line in a file.
    """
    file_fo = codecs.open(filename, 'r', 'utf-8')
    lines = file_fo.readlines()
    file_fo.close()

    return lines


def read_stopwords():
    """
    Reads the initial stop word list.
    """
    stopword_file = otcore_settings.INITIAL_FILE_STOPWORDS
    stopwords = lines_in_file(stopword_file)

    for stop in stopwords:
        if stop.strip():
            StopWord.objects.get_or_create(word=stop.strip())


def read_recognizers():
    recognizers = importlib.import_module(otcore_settings.INITIAL_FILE_RECOGNIZERS).recognizers

    for recognizer in enumerate(recognizers):
        Recognizer.objects.get_or_create(
            **recognizer[1],
            defaults={ 
                'priority': recognizer[0]
            }
        )
