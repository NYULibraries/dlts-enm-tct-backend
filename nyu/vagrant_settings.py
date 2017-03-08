import os
from nyu.settings import *

STATIC_ROOT = '/vagrant/nyu/static'
MEDIA_ROOT = '/vagrant/nyu/media'
# Epub config settings
EPUB_SOURCES_FOLDER = os.path.join(MEDIA_ROOT, 'epubs')
EPUB_UPLOAD_FOLDER = EPUB_SOURCES_FOLDER
EPUB_DECOMPRESSED_FOLDER = os.path.join(MEDIA_ROOT, 'epub_decompressed')
MEDIA_URL = '/media/'


DEBUG = True
DJANGO_DEBUG_TOOLBAR = True

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True

INSTALLED_APPS += ['debug_toolbar',]

def custom_show_toolbar(self):
    return True

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
}
# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'otlnyu_db',
        # 'NAME': 'nyu_refactor_db',
        'USER': 'postgres',
        'PASSWORD': 'password:',
        'HOST': 'localhost',

    }
}

EDITORIAL_INTERFACE_SERVER = 'http://localhost:9000/#'

REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = ['rest_framework.permissions.AllowAny']
