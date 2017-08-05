import os
import importlib

from django.conf import settings
from django.test.signals import setting_changed

DEFAULTS = {
    # Scope
    'SCOPE_SEPARATOR': '_',
    'SCOPE': 'Generic',

    # Automatic Processing Rules
    'LOCAL_CONTAINMENT': False,
    'LOCAL_MULTIPLE_TOKENS': False,
    'MULTIPLE_RELATIONS_COUNT': 3,
    'AUTOMATIC_RELATIONTYPES': ['MultipleTokens', 'Containment'],

    # View Data
    'BASKET_TRANSFORMER': 'otcore.hit.processing.BasketTransformer',

    # Slugification
    'WHOLE_NAME_TOKENIZERS': [],
    'SINGLE_WORD_TOKENIZERS': ['otcore.lex.recognizers.stemmer'],
    'CACHE_STOPWORDS': True,
    'CACHE_RECOGNIZERS': True,
    'INITIAL_FILE_STOPWORDS': os.path.join(settings.BASE_DIR, 'otcore', 'lex', 'initial', 'stopwords.txt'),
    'INITIAL_FILE_RECOGNIZERS': 'otcore.lex.initial.recognizers',
}

IMPORT_STRINGS = (
    'BASKET_TRANSFORMER',
    'WHOLE_NAME_TOKENIZERS',
    'SINGLE_WORD_TOKENIZERS',
)


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item) for item in val]
    return val


def import_from_string(val):
    """
    Attempt to import a class from a string representation.  Lifted from django-rest-framework
    """
    try:
        # Nod to tastypie's use of importlib.
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        msg = "Could not import '%s'. %s: %s." % (val, e.__class__.__name__, e)
        raise ImportError(msg)


class OTCoreSettings:
    """
    Settings Class settings to be cached, so string imports don't have to be 
    re-imported with every access.  This module is HEAVILY inspired by django-rest-framework's
    settings module
    """
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'OTCORE', {})
        return self._user_settings
    
    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        setattr(self, attr, val)
        return val


otcore_settings = OTCoreSettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_otcore_settings(*args, **kwargs):
    global octore_settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == 'OTCORE':
        otcore_settings = APISettings(value, DEFAULTS, IMPORT_STRINGS)


setting_changed.connect(reload_otcore_settings)
