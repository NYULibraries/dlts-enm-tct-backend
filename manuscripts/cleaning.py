from django.db.models import Q
from django.db import IntegrityError

from otcore.hit.models import Hit
from otcore.hit.processing import merge_baskets


def full_clean():
    remove_whitespace()
    replace_smart_quotes()
    remove_trailing_commas()
    remove_unopened_parens()
    remove_formatted_indent()
    remove_trailing_double_dash()


def remove_whitespace():
    hits = Hit.objects.filter(
        Q(name__startswith=" ") |
        Q(name__endswith=" "))

    for hit in hits:
        name = hit.name.strip()
        check_save(hit, name)


def replace_smart_quotes():
    hits = Hit.objects.filter(
        Q(name__contains='“') |
        Q(name__contains='’') |
        Q(name__contains='”'))

    for hit in hits:
        name = hit.name.replace('“', '"').replace('”', '"').replace('’', "'")
        check_save(hit, name)


def remove_trailing_commas():
    hits = Hit.objects.filter(name__endswith=',')

    for hit in hits:
        name = hit.name[:len(hit.name)-1]
        check_save(hit, name)

    hits = Hit.objects.filter(name__endswith=',"')

    for hit in hits:
        name = hit.name.replace(',"', '"')
        check_save(hit, name)


def remove_unopened_parens():
    hits = Hit.objects.filter(name__endswith=')').exclude(name__contains='(')

    for hit in hits:
        name = hit.name[:len(hit.name)-1]
        check_save(hit, name)


def remove_formatted_indent():
    hits = Hit.objects.filter(name__contains='—\t')

    for hit in hits:
        name = hit.name.replace('—\t', '')
        check_save(hit, name)


def remove_trailing_double_dash():
    hits = Hit.objects.filter(name__endswith=' --')
    
    for hit in hits:
        name = hit.name[:len(hit.name)-3]
        check_save(hit, name)


def check_save(hit, new_name):
    """
    Avoids duplication when saving new hit names.
    If the new name already exists and has a different basket, merge the baskets
    and delete the old hit. 
    If the new name already exists and has the same basket, just delete the old hit.
    Otherwise, just rename and save
    """
    # print("{} | {}".format(hit.name, new_name))
    try:
        new_name_hit = Hit.objects.get(name=new_name)
    except Hit.DoesNotExist:
        hit.name=new_name
        hit.save()
        hit.basket.save() # force basket name to update
    else:
        if hit.basket != new_name_hit.basket:
            merge_baskets(hit.basket, new_name_hit.basket)

        hit.delete()
        new_name_hit.basket.save() # force basket name to update
