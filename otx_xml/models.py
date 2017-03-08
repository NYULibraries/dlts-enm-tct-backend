from django.db import models


class XMLPattern(models.Model):
    """
    Model to hold XML extraction patterns for BaseXMLExtractor
    """
    name = models.CharField(max_length=255, blank=True, unique=True, default='default')

    xpath_title = models.CharField(max_length=255, blank=True)
    xpath_author = models.CharField(max_length=255, blank=True)

    xpath_locations = models.CharField(max_length=255, blank=True)

    # Note that the following xpaths are assumed to be relative to each individual location
    xpath_location_localid = models.CharField(max_length=255, blank=True)
    xpath_content = models.CharField(max_length=255, blank=True)
    xpath_content_header = models.CharField(max_length=255, blank=True)

    xpath_topic = models.CharField(max_length=255, blank=True)
    xpath_occurrence = models.CharField(max_length=255, blank=True)
