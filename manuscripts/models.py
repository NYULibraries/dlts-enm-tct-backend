import os

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

from otx_epub.models import Epub
from otcore.occurrence.models import Document


class IndexPattern(models.Model):
    name = models.CharField(max_length=255, unique=True, default='default')
    description = models.TextField(blank=True)

    # Pages are sliced using string operations
    # pagenumber_pre_string holds the surround tag text BEFORE the pagenumber
    pagenumber_pre_strings = ArrayField(
        models.CharField(max_length=50, blank=True),
    )
    pagenumber_css_selector_pattern = models.CharField(max_length=100, blank=True)
    pagenumber_xpath_pattern = models.CharField(max_length=100, blank=True)
    pagenumber_tag_pattern = models.CharField(max_length=100, blank=True)

    # xpath to locate main entries
    xpath_entry = models.CharField(max_length=255, blank=True)

    # Strings to separate see and see also
    see_split_strings = ArrayField(
        models.CharField(max_length=50, blank=True)
    )
    see_also_split_strings = ArrayField(
        models.CharField(max_length=50, blank=True),
    )
    # element names that contain sees and seealso
    xpath_see = models.CharField(max_length=50, blank=True)
    xpath_seealso = models.CharField(max_length=50, blank=True)

    # If there are multiple see or seealso reference, this divides them
    separator_between_sees = models.CharField(max_length=50, blank=True)
    separator_between_seealsos = models.CharField(max_length=50, blank=True)

    # Indicates that a see entry points to a subentry
    separator_see_subentry = models.CharField(max_length=50, blank=True)

    # for parsing see and seealso embedded inside inline subentries
    inline_see_start = models.CharField(max_length=50, blank=True)
    inline_see_also_start = models.CharField(max_length=50, blank=True)
    inline_see_end = models.CharField(max_length=50, blank=True)
    inline_see_also_end = models.CharField(max_length=50, blank=True)

    # This field both tells the parser IF the subentries are a separate element
    # AND what the class of that separate subentry is
    subentry_classes = ArrayField(
        models.CharField(max_length=50, blank=True)
    )

    # This field both tells the parser IF the entry has inline subentries
    # and what separator is used between them
    separator_between_subentries = models.CharField(max_length=50, blank=True)

    # Some entries are separated from occurrences by a comma, or some other characters. Blanks are ignored.
    separator_between_entry_and_occurrences = models.CharField(max_length=50, blank=True)

    # how to find occurrences in an entry
    xpath_occurrence_link = models.CharField(max_length=150, blank=True)
   
    # Used when subentry and main entry are on the same line
    # (Generally when the main entry has no occurrences)
    separator_before_first_subentry = models.CharField(max_length=50, blank=True)


    indicators_of_occurrence_range = ArrayField(
        models.CharField(max_length=50, default='-')
    )

    def pagenumber_selector_from_location(self, location):
        return self.pagenumber_css_selector_pattern.format(location.localid.split('_')[1])

    def pagenumber_tag_from_location(self, location):
        return self.pagenumber_tag_pattern.format(location.localid.split('_')[1])

    def pagenumber_xpath_from_location(self, location):
        return self.pagenumber_xpath_pattern.format(location.localid.split('_')[1])

    def __str__(self):
        return self.name


class Index(models.Model):
    # Location to actual index file
    relative_location = models.CharField(max_length=128)
    epub = models.ForeignKey(Document, models.CASCADE, related_name="inedexes")
    indexpattern = models.ForeignKey(IndexPattern, related_name="indexes", blank=True, null=True)

    @property
    def url(self):
        return os.path.join(settings.MEDIA_URL, self.relative_location)

    @property
    def path(self):
        return os.path.join(settings.MEDIA_ROOT, self.relative_location)

    def save(self, *args, **kwargs):
        if self.relative_location[0] == '/':
            self.relative_location = self.relative_location[1:]

        return super(Index, self).save(*args, **kwargs)

