import os

from django.db import models
from django.contrib.auth.models import User

from otcore.hit.models import Basket


class Review(models.Model):
    basket = models.OneToOneField(Basket)
    time = models.DateTimeField(blank=True, null=True)
    reviewer =  models.ForeignKey(User, related_name='reviewed', blank=True, null=True)

    reviewed = models.BooleanField(default=False)
    changed = models.BooleanField(default=False)

    @property
    def status(self):
        if not self.reviewed:
            return "Not Reviewed"
        else:
            if self.changed:
                return "Reviewed, Changed"
            else:
                return "Reviewed, Unchanged"


def create_review(sender, instance, created, **kwargs):
    """
    Create Review Model for every new Basket Model
    """
    if created:
        Review.objects.create(basket=instance)


models.signals.post_save.connect(
    create_review, sender=Basket, weak=False, dispatch_uid='models.create_view'
)


class Report(models.Model):
    """
    Class for tracking generated reports of Review
    """
    time = models.DateTimeField(auto_now_add=True)

    ALL_TOPICS = 'A'
    ALL_REVIEWED = 'R'
    UNCHANGED = 'U'
    CHANGED = 'C'

    TOPIC_SETS = (
        (ALL_TOPICS, 'All Topics'),
        (ALL_REVIEWED, 'All Reviewed Topics'),
        (UNCHANGED, 'Reviewed But Unchanged Topics Only'),
        (CHANGED, 'Reviewed and Changed Topics Only')
    )

    topic_set = models.CharField(max_length=1, choices=TOPIC_SETS)
    location = models.FileField(upload_to='reports')

    def __str__(self):
        return self.location.name


def delete_report_file(sender, instance, **kwargs):
    """
    Function to handle deleting of the actual Report file
    before deleting the database instance
    """
    os.remove(instance.location.path)


models.signals.post_delete.connect(
    delete_report_file, sender=Report, weak=False, dispatch_uid='models.delete_report_file'
)
