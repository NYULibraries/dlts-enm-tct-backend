from .settings import *
import os
import json

ALLOWED_HOSTS = ['69.30.245.221', '69.30.245.218', 'nyuapi.infoloom.nyc']
STATIC_ROOT = '/www/nyu.infoloom.nyc/static/'
MEDIA_ROOT = '/www/nyu.infoloom.nyc/media/'
# MEDIA_SERVER = 'http://localhost:8000/media'
# Epub config settings
EPUB_SOURCES_FOLDER = os.path.join(MEDIA_ROOT, 'epubs')
EPUB_UPLOAD_FOLDER = EPUB_SOURCES_FOLDER
EPUB_DECOMPRESSED_FOLDER = os.path.join(MEDIA_ROOT, 'epub_decompressed')

MEDIA_URL = '/media/'


DEBUG = False 
DJANGO_DEBUG_TOOLBAR = False

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nyuotl_db',
        'USER': 'postgres',
        'PASSWORD': 'cFHg*Liw45(',
        'HOST': 'localhost',
    }
}

REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = ['rest_framework.permissions.IsAuthenticatedOrReadOnly']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'watched_file': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/django/nyu.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['watched_file',],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
