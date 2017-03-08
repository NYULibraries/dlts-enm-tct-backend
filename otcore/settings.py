from django.conf import settings

DEFAULTS = {
    'INITIAL_FILE_STOPWORDS': None,
    'INITIAL_FILE_ACRONYMS': None,
    'INITIAL_FILE_EXPRESSIONS': None,
    'INITIAL_FILE_IRREGULARS': None,
    'INITIAL_FILE_ERRORS': None,
    'SCOPE_SEPARATOR': '_',
    'SCOPE': 'Generic',
    'LOCAL_CONTAINMENT': False,
    'LOCAL_MULTIPLE_TOKENS': False,
    'MULTIPLE_RELATIONS_COUNT': 3,
    'AUTOMATIC_RELATIONTYPES': ['MultipleTokens', 'Containment'],
    'ENGLISH_GRAMMAR': True,
    'SPLIT_ON_PUNCTUATION': True
}


def setting(name):
    return getattr(settings, name, DEFAULTS[name])
