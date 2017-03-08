import os

from django.core.management import call_command
from django.db.models import Count

from otx_epub.models import Epub
from otcore.hit.models import Hit, Basket
from otcore.occurrence.models import Occurrence
from otcore.relation.models import RelatedBasket
from otcore.topic.models import Tokengroup

from initial.pattern_overrides import pattern_overrides
from manuscripts.extractors import IndexExtractor


EXCLUDE_TITLES = [
    # 'Negrophobia and Reasonable Racism',
    # 'Narcissism and the Literary Libido',
    'Framed: The New Woman Criminal in British Culture at the Fin de Siecle',
    'Originality, Imitation, and Plagiarism',
    'Civic Engagement in the Wake of Katrina',
    'Parodies of Ownership: Hip-Hop Aesthetics and Intellectual Property Law',
]


def clear():
    Basket.objects.all().delete()
    Hit.objects.all().delete()
    Occurrence.objects.all().delete()
    RelatedBasket.objects.all().delete()
    Tokengroup.objects.all().delete()


def run():
    call_command('loaddata', 'indexpatterns')

    # for epub in Epub.objects.filter(publisher='UMP1').exclude(title__in=EXCLUDE_TITLES):
    for epub in Epub.objects.all():
        print("{} ({})".format(epub.title.upper(), os.path.basename(epub.contents)))
        clear()
        IndexExtractor.extract_from_source(epub, extract_locations=False)
        print("Hits: {}".format(Hit.objects.count()))
        print("Baskets: {}".format(Basket.objects.count()))
        print("Occurrences: {}".format(Occurrence.objects.count()))

        print("Baskets with no occurrences:")
        for basket in Basket.objects.annotate(c=Count('occurs')).filter(c=0):
            print("... {}".format(basket.display_name))
