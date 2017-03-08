import os

STATIC_ROOT = '/home/michel/e/projects/django/static/nyu'
MEDIA_ROOT = '/home/michel/e/projects/django/media/nyu'
MEDIA_SERVER = 'http://localhost:8000/media'

# Epub config settings
EPUB_UPLOAD_FOLDER = 'epubs'
EPUB_SOURCES_FOLDER = os.path.join(MEDIA_ROOT, EPUB_UPLOAD_FOLDER)
EPUB_DECOMPRESSED_FOLDER = MEDIA_ROOT + '/epub_decompressed'
MEDIA_URL = '/media/'
EPUB_DECOMPRESSED_URL = MEDIA_URL + 'epub_decompressed/'
EPUB_PROCESSED_FOLDER = MEDIA_ROOT + '/epub_processed'
EPUB_INDEXES_FOLDER = MEDIA_ROOT + '/epub_indexes'



DEBUG = True
DJANGO_DEBUG_TOOLBAR = True

SECRET_KEY = '6vy&$1yrs+m8n8hxt0%8)b=r0#6a&xm(o^j3%i%k8)b#@0bioe'

# CORS settings
CORS_ORIGIN_ALLOW_ALL = True


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
        'USER': 'postgres',
        'PASSWORD': 'password:',
        'HOST': 'localhost',

    }
}
EDITORIAL_INTERFACE_SERVER='http://localhost:9000/#'
from .settings import *
