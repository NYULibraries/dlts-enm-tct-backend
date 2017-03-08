from django.shortcuts import render
from django.db.models import Q
from django.db.utils import IntegrityError
from otcore.hit.models import Hit
from otcore.relation.models import RelatedHit, RelatedBasket
from otcore.occurrence.models import Occurrence
from otcore.settings import setting


def detach(hit, old_basket, split_data):
    """
    Detach hit from basket.
    This amounts to "unsynonymize"
    Make another basket just for hit.
    This will only work if there is more than one hit for this basket.

    if basket has only one hit:
        do nothing

    if basket has more than one hit:
        if slug_scopeid for detached hit is different from basket label, use it for new basket.
        if slug_scopeid for detached hit is the same as basket label, modify the basket label to correspond to another slug_scopeid (for another name)

    """

    # Remove hit from basket
    hit.basket = None
    hit.hidden = False
    hit.save()

    # rename label to avoid potential labelling conflicts
    some_hit = old_basket.topic_hits.all()[0]
    new_label = '%s%s%s' % (some_hit.slug, setting('SCOPE_SEPARATOR'), some_hit.scope.id)
    if new_label != old_basket.label:
        old_basket.label = new_label
        old_basket.save()

    # create new basket on detached hit
    hit.create_basket_if_needed(force=True)

    new_basket = hit.basket

    # handle occurrence splits
    split_non_m2m_field(
        old_basket.occurs.all().order_by('id').distinct('id'),
        split_data['occurrences'],
        old_basket,
        new_basket,
        'basket'
    )

    # handle from relation splits
    split_non_m2m_field(
        old_basket.from_relations.filter(forbidden=False).order_by('id').distinct('id'),
        split_data['relations'],
        old_basket,
        new_basket,
        'source'
    )

    # handle to relation splits
    split_non_m2m_field(
        old_basket.to_relations.filter(forbidden=False).order_by('id').distinct('id'),
        split_data['relations'],
        old_basket,
        new_basket,
        'destination'
    )

    # handle type split
    if split_data.get('types', None) is not None:
        split_m2m_field(
            old_basket.types.all().order_by('id').distinct('id'),
            split_data['types'],
            old_basket,
            new_basket,
            'types'
        )

    old_basket.tokengroups.clear()
    old_basket.local_tokengroup()
    new_basket.local_tokengroup()

    # manually trigger saves to update the display_name propert
    old_basket.save()
    new_basket.save()

    return old_basket, new_basket


def duplicate_except_one(old_instance, non_dupe_field, non_dupe_value):
    """
    Duplicates a moodel except for one field (passed as a string into
    the non_dupe_field arg, and set to the value in non_dupe_value)
    Returns the new model instance
    """
    instance = old_instance.__class__()

    fields = instance._meta.get_fields()
    local_fields = [x for x in fields if not x.many_to_many and not x.auto_created]
    m2m_fields = [x for x in fields if x.many_to_many]

    for field in local_fields:
        if field.name == 'id':
            pass
        elif field.name == non_dupe_field:
            setattr(instance, non_dupe_field, non_dupe_value)
        else:
            old_value = getattr(old_instance, field.name)
            setattr(instance, field.name, old_value)

    instance.save()

    for field in m2m_fields:
        old_values = getattr(old_instance, field.name).all()
        getattr(instance, field.name).add(*old_values)

    return instance


def split_non_m2m_field(field_queryset, field_split_data, old_basket, new_basket, set_field):
    """
    Takes a queryset of all the instances of a related field (field_query).
    """
    for instance in field_queryset:
        print("{0}: {1}".format(set_field, instance.id))
        if field_split_data[str(instance.id)] == 'stay':
            pass
        elif field_split_data[str(instance.id)] == 'move':
            setattr(instance, set_field, new_basket)
            instance.save()
        elif field_split_data[str(instance.id)] == 'both':
            duplicate_except_one(instance, set_field, new_basket)


def split_m2m_field(field_queryset, field_split_data, old_basket, new_basket, set_field):
    for instance in field_queryset:
        print("{0}: {1}".format(set_field, instance.id))
        if field_split_data[str(instance.id)] == 'stay':
            pass
        elif field_split_data[str(instance.id)] == 'move':
            getattr(old_basket, set_field).remove(instance)
            getattr(new_basket, set_field).add(instance)
        elif field_split_data[str(instance.id)] == 'both':
            getattr(new_basket, set_field).add(instance)


def merge_baskets(basket_discarded, basket_remaining):
    for hit in basket_discarded.topic_hits.all():
        hit.basket = basket_remaining
        hit.save()
    # Types & weblinks for basket2 redirected to basket1
    for ttype in basket_discarded.types.all():
        basket_remaining.types.add(ttype)

    # Occurrences for basket2 get redirected to basket1
    # Unless an occurrence for that relation already exists
    for occ in basket_discarded.occurs.all():
        occ.basket = basket_remaining
        occ.save()

        # TODO: This seems like unecessary database hits: fix so that it just fetches the 
        # basket remains occurrences once instead of rechecking each time
        if Occurrence.objects.filter(basket=occ.basket, location=occ.location).count() > 1:
            occ.delete()

    # Delete relations between the merged baskets
    RelatedBasket.objects.filter(source=basket_discarded, destination=basket_remaining).delete()
    RelatedBasket.objects.filter(source=basket_remaining, destination=basket_discarded).delete()

    relations = list(basket_discarded.from_relations.all()) + list(basket_discarded.to_relations.all())

    existing_relations = [(x.source_id, x.relationtype_id) for x in basket_remaining.to_relations.all()] + [(x.destination_id, x.relationtype_id) for x in basket_remaining.from_relations.all()]
    for relation in relations:
        if relation.source == basket_remaining or relation.destination == basket_remaining:
            relation.delete()
        else:
            if relation.source == basket_discarded:
                if (relation.destination_id, relation.relationtype_id) not in existing_relations:
                    relation.source = basket_remaining
                    relation.save()
                    existing_relations.append((relation.destination_id, relation.relationtype_id))
                else:
                    relation.delete()
            else:
                if (relation.source_id, relation.relationtype_id) not in existing_relations:
                    relation.destination = basket_remaining
                    relation.save()
                    existing_relations.append((relation.source_id, relation.relationtype_id))
                else:
                    relation.delete()


    # tokengroups are recalculated for the merged basket.
    basket_remaining.local_tokengroup()

    basket_discarded.delete()

    return basket_remaining
