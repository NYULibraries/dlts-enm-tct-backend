import re

from django.core.cache import cache

from otcore.settings import otcore_settings
from .models import Recognizer, recache_recognizers


def load_recognizers():
    """
    Fetches recognizers from cache, if CACHE_RECOGNIZERS is True.
    Minimizes roundtrip database fetches for slugification
    """
    if otcore_settings.CACHE_RECOGNIZERS:
        recognizers = cache.get('recognizers')
      
        if recognizers is None:
            recognizers = recache_recognizers()

    else:
        recognizers = list(Recognizer.objects.all())

    return recognizers


def stemmer(word):
    """
    If a recognizer pattern matches the word, perform the replacement and return the new word.
    Otherwise return the unaltered word
    """
    recognizers = load_recognizers()

    for recognizer in recognizers:
        word, count = re.subn(recognizer.recognizer, recognizer.replacer, word, flags=re.U)

        if count > 0 and not recognizer.passthrough:
            return word

    return word
