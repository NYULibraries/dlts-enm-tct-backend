from django.db import models
from django.core.urlresolvers import reverse
import importlib


class StopWord(models.Model):

    """
    Stop words will be discarded and will not be transformed into tokens.
    """

    word = models.CharField(max_length=500, unique=True, db_index=True)

    def __str__(self):
        return self.word

    def get_absolute_url(self):
        return reverse('alt-stopword-update', args=[self.id])

    class Meta:
        ordering = ('word',)


class Acronym(models.Model):

    """
    This is a translation table between acronyms and their developed forms.
    Acronyms are expanded for merging purposes, when present into a string.
    Some acronyms (e.g. "AS" for "American Samoa") may be in conflict with
    "as" if "as" is declared as a stop word.
    """

    acronym = models.CharField(max_length=20, unique=True)
    developed = models.CharField(max_length=500, blank=False)
    active = models.BooleanField(default=True)
    rationale = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.acronym

    def get_absolute_url(self):
        return reverse('alt-acronym-update', args=[self.id])

    class Meta:
        ordering = ('acronym', )


class Expression(models.Model):

    """
    Expressions are sequences of words that need to be kept together,
    because they lose their meaning in isolation. For example, "United States"
    or "Real Estate". If they would not be declared as exception, "Real Estate" for
    example would be tokenized into two tokens, "real" and "estate", therefore
    opening the door to merging with other topic names that would contain "estate",
    and that wouldn't make sense.
    """

    expression = models.CharField(max_length=500, unique=True, db_index=True)

    def __str__(self):
        return self.expression

    def get_absolute_url(self):
        return reverse('alt-expression-update', args=[self.id])

    class Meta:
        ordering = ('expression',)


class Irregular(models.Model):

    """
    List of words, manually transformed into tokens.
    This list includes irregular plural, as well as any word
    that needs to be transformed into a token.
    """

    word = models.CharField(max_length=255, unique=True, db_index=True)
    token = models.CharField(max_length=255)

    @property
    def slug(self):
        return self.token

    def __str__(self):
        return self.word

    class Meta:
        ordering = ('word',)
        unique_together = (('word', 'token'))
