from django.db import models

from otcore.settings import setting


class RelationType(models.Model):

    """
    rtype stands for: 'relation type'
    """

    rtype = models.CharField(max_length=100, unique=True, null=False, default='Generic')
    description = models.TextField(blank=True, null=True)
    role_from = models.CharField(max_length=100, default='Generic')
    role_to = models.CharField(max_length=100, default='Generic')
    symmetrical = models.BooleanField(default=True)

    def __str__(self):
        return self.rtype

    class Meta:
        ordering = ('rtype',)
        unique_together = (('rtype', 'role_from', 'role_to'))

    # TODO. Validation. If role_from and role_to are identical, then symmetrical is True. And vice-versa.


def get_default_type():
    return RelationType.objects.get_or_create(rtype="Generic")[0].id


class RelatedBasketQuerySet(models.QuerySet):
    """
    Custom Queryset for RelatedBasket to create new deletion tools
    On deletion, it will check the RelationType.  If it's an automatically generated RelationType
    (as specified by settings), the RelatedBasket is kept with forbidden=true set.  Otherwise,
    RelatedBasket is deleted.
    """
    def check_delete(self):
        for obj in self.select_related('relationtype'):
            obj.check_delete()


class RelatedBasket(models.Model):

    relationtype = models.ForeignKey(RelationType, default=get_default_type, on_delete=models.SET_DEFAULT, related_name='related_baskets')
    forbidden = models.BooleanField(default=False)
    source = models.ForeignKey('hit.Basket', related_name='from_relations', on_delete=models.CASCADE)
    destination = models.ForeignKey('hit.Basket', related_name='to_relations', on_delete=models.CASCADE)

    objects = RelatedBasketQuerySet.as_manager()

    def __str__(self):
        return '%s: %s......%s' % (self.relationtype, self.source.label, self.destination.label)

    class Meta:
        ordering = ('relationtype', 'source', 'destination')
        unique_together = (('relationtype', 'source', 'destination'))

    def check_delete(self, *args, **kwargs):
        if self.relationtype.rtype in setting('AUTOMATIC_RELATIONTYPES'):
            self.forbidden = True
            self.save()
        else:
            self.delete()


class RelatedHit(models.Model):

    relationtype = models.ForeignKey(RelationType, blank=True, default=get_default_type, on_delete=models.SET_DEFAULT)
    forbidden = models.BooleanField(default=False)
    source = models.ForeignKey('hit.Hit', related_name='from_hit', on_delete=models.CASCADE)
    destination = models.ForeignKey('hit.Hit', related_name='to_hit', on_delete=models.CASCADE)

    def __str__(self):
        return '%s ....... %s' % (self.source, self.destination)

    class Meta:
        ordering = ('relationtype', 'source', 'destination')
        unique_together = (('relationtype', 'source', 'destination'))
