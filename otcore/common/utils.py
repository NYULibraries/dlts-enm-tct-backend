import importlib

from django.db.models import Max, Count


def clean_duplicates(queryset, unique_fields):
    """
    Code for cleaning out duplicate models
    Thanks to:
    http://stackoverflow.com/questions/13700200/django-remove-duplicate-objects-where-there-is-more-than-one-field-to-compare
    """
    
    duplicates = (queryset.values(*unique_fields).order_by().annotate(
            max_id=Max('id'),
            count_id=Count('id')
        ).filter(count_id__gt=1))
    
    index = 1
    total = len(duplicates)
    for duplicate in duplicates:
        (queryset.filter(**{x: duplicate[x] for x in unique_fields})
            .exclude(id=duplicate['max_id'])
            .delete())
        index += 1
