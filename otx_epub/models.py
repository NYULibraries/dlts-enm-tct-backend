from django.db import models
from django.conf import settings

from otcore.occurrence.models import Document
from .storage import OverwriteStorage


class Epub(Document):
    publisher = models.CharField(max_length=255, blank=True)

    source = models.FileField(
        upload_to=settings.EPUB_UPLOAD_FOLDER,
        storage=OverwriteStorage()
    )
    contents = models.CharField(max_length=255, blank=True)
    oebps_folder = models.CharField(max_length=255, blank=True)
    manifest = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title
