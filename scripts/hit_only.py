import os

from django.core.management import call_command
from django.db.models import Count
from django.utils import timezone

from otx_epub.models import Epub
from otcore.hit.models import Hit, Basket
from otcore.occurrence.models import Occurrence
from otcore.relation.models import RelatedBasket

from manuscripts.extractors import IndexExtractor
from manuscripts.cleaning import full_clean


def run():
    Basket.objects.all().delete()
    Hit.objects.all().delete()
    Occurrence.objects.all().delete()
    RelatedBasket.objects.all().delete()

    # Load predefined indexpatterns
    call_command('loaddata', 'indexpatterns')

    start = timezone.now()
    epub = Epub.objects.get(title="My Life as a Night Elf Priest")
    IndexExtractor.extract_from_source(epub, extract_locations = False)

    end = timezone.now()

    full_clean()

    print("Hits: {}".format(Hit.objects.count()))
    print("Baskets: {}".format(Basket.objects.count()))
    print("Occurrences: {}".format(Occurrence.objects.count()))

    print("Baskets with no occurrences:")
    for basket in Basket.objects.annotate(c=Count('occurs')).filter(c=0):
        print("... {}".format(basket.display_name))

    print("Processing time: {}".format(end-start))
