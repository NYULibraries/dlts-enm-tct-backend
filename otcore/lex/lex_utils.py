# -- coding: utf-8 --
from __future__ import unicode_literals
import unicodedata

from django.conf import settings
from django.utils.text import slugify
from django.core.cache import cache

from otcore.lex.models import StopWord, Recognizer, recache_stopwords
from otcore.settings import otcore_settings


def lex_slugify(value):
    for tokenizer in otcore_settings.WHOLE_NAME_TOKENIZERS:
        value = tokenizer(value)

    # Perform django slugifiction
    words = clean_words(value)

    slug_set = run_tokenizers(words) 
    slug_list = extract_stopwords(slug_set)

    slug_value = '-'.join(sorted(slug_list))
    return slug_value.strip('-')


def run_tokenizers(words):
    """
    Iterate through tokenizers. If the produced token has a hyphen, split and recursively move
    process the new tokens
    """
    slug_set = set()
    for word in list(words):
        for tokenizer in otcore_settings.SINGLE_WORD_TOKENIZERS:
            word = tokenizer(word)

        if '-' in word:
            slug_set |= run_tokenizers(word.split('-'))
        else:
            slug_set.add(word)

    return slug_set


def clean_words(value):
    """
    replacement for django's slugify.  For various reasons, we don't want to 
    strip out all punctuation at this stage, so this just cleans and splits
    """
    value = unicodedata.normalize('NFKC', value)
    return set([word.strip() for word in value.strip().lower().split()])


def load_stopwords():
    """
    Fetches stopwords from cache, if CACHE_STOPWORDS is True.
    """
    if otcore_settings.CACHE_RECOGNIZERS:
        stopwords = cache.get('stopwords')
      
        if stopwords is None:
            stopwords = recache_stopwords()

    else:
        stopwords = StopWord.objects.values_list('word', flat=True) 

    return set(stopwords)
    

def extract_stopwords(slug_set):
    stopwords = load_stopwords()

    minus_stopwords = slug_set.difference(stopwords)
    # If there is nothing left after stopwords are removed, ignore the stopwords altogether.
    if len(minus_stopwords):
        slug_list = list(minus_stopwords)
    else:
        slug_list = list(slug_set)

    return slug_list
