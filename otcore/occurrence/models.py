from django.db import models
from otcore.hit.models import Basket

import os


class Document(models.Model):

    """
    A "document" instance uniquely identifies an abstract document,
    by its title, author, and points to its document class.
    """

    title = models.TextField(null=True, blank=True)
    author = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return '%s' % self.id

    def delete(self):
        """
        Overwritten delete function also removes baskets with no occurrences other than those
        from the deleted document
        """
        # Get all Baskets with Occurrences from this Document
        baskets = Basket.objects.filter(occurs__location__document=self).order_by('basket_id').prefetch_related('occurs', 'occurs__location').order_by('id').distinct('id')

        # Find the baskets in that group that have no other occurrences
        basket_to_delete_ids = []
        for basket in baskets:
            c = basket.occurs.filter(location__isnull=False).exclude(location__document=self).count()
            if c == 0:
                basket_to_delete_ids.append(basket.id)

        # Delete those baskets
        print("{} Baskets deleted.".format(len(basket_to_delete_ids)))
        Basket.objects.filter(id__in=basket_to_delete_ids).delete()

        # Delete Associated Content
        print("{} Content objects deleted".format(Content.objects.filter(at_location__document=self).count()))
        Content.objects.filter(at_location__document=self).delete()

        return super(Document, self).delete()


class Location(models.Model):

    """
    A location is either a file or a specific location in a file (if localid is not null).
    """

    sequence_number = models.IntegerField(null=True, blank=True)
    filepath = models.TextField(max_length=255)
    localid = models.CharField(max_length=255, blank=True, null=True)
    document = models.ForeignKey('Document', related_name='locations', null=True, blank=True, on_delete=models.CASCADE)
    content = models.ForeignKey('Content', related_name='at_location', null=True, blank=True, on_delete=models.SET_NULL)
    context = models.CharField(max_length=255, blank=True, null=True)

    @property
    def extension(self):
        return self.filepath.rsplit('.', 1)[-1]

    @property
    def prefix(self):
        return os.path.basename(self.filepath).rsplit('.', 1)[0]

    def __str__(self):
        if self.localid:
            return '%s#%s' % (self.filepath, self.localid)
        else:
            return '%s' % self.filepath

    @property
    def next_location_id(self):
        try:
            next_loc = Location.objects.get(document=self.document, sequence_number=self.sequence_number + 1).id
        except Location.DoesNotExist:
            next_loc = None
        return next_loc

    @property
    def previous_location_id(self):
        try:
            prev_loc = Location.objects.get(document=self.document, sequence_number=self.sequence_number - 1).id
        except Location.DoesNotExist:
            prev_loc = None
        return prev_loc

    class Meta:
        ordering = ['sequence_number']
        unique_together = (('localid', 'filepath'),)


class Content(models.Model):

    # Content unique indicator is what uniquely defines a content.
    content_unique_indicator = models.CharField(max_length=55, unique=True, blank=True, null=True)
    content_descriptor = models.CharField(max_length=255, blank=True)
    text = models.TextField()

    @property
    def excerpt(self):
        return '%s...' % self.text[:25]

    def __str__(self):
        return '%s...' % (self.text[:25])

    def save(self, *args, **kwargs):
        if not self.content_unique_indicator:
            self.content_unique_indicator = None

        return super(Content, self).save(*args, **kwargs)


class Occurrence(models.Model):
    """
    Logical occurrence. It points to up to 3 physical locations:
    Input, Output, and Processing.
    """

    location = models.ForeignKey(Location, null=True, blank=True, related_name='occurrences', on_delete=models.CASCADE)

    hit_in_content = models.CharField(max_length=25, null=True, blank=True, default='Not Found')

    basket = models.ForeignKey('hit.Basket', related_name='occurs', null=True, blank=True, on_delete=models.CASCADE)

    @property
    def other_baskets(self):
        other_basket_list = Basket.objects.filter(occurs__location=self.location).exclude(id=self.basket.id).order_by('id').distinct('id').prefetch_related('topic_hits')

        baskets = sorted(other_basket_list, key=lambda x: x.preferred_topic_name.lower())

        return baskets

    class Meta:
        order_with_respect_to = 'location'

    def __str__(self):
        return '%s' % (self.id)
