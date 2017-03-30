from django.db import models
from django.core.urlresolvers import reverse


class Tokengroup(models.Model):

    """
    The token groups are used to group tokens that are part of the
    augmented slugs (tid = name slug + synonym slug ) that will be used to
    build automatic relationships based on a certain number of tokens
    in common.
    """

    group = models.CharField(max_length=1500, unique=True)

    def __str__(self):
        return self.group

    class Meta:
        ordering = ('group',)


class Ttype(models.Model):

    """
    Topic Type
    """

    ttype = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.ttype


