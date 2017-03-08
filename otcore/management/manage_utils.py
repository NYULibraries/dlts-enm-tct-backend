import os
import subprocess

from django.conf import settings
from otcore.occurrence.models import Occurrence, Document, Location, Content
from otcore.relation.models import RelationType, RelatedHit, RelatedBasket
from otcore.topic.models import Tokengroup
from otcore.hit.models import Hit, Basket, Scope

from otcore.lex.processing import read_stopwords


def initialize():

    # Create Media directory for the database, if it doesn't exist
    try:
        os.makedirs(settings.MEDIA_ROOT)
    except OSError:
        pass    # Directory already exists.

    # Deleting Existing Data if any.
    print('Deleting existing data')
    for x in RelatedHit.objects.all():
        x.delete()
    for x in RelatedBasket.objects.all():
        x.delete()
    for x in RelationType.objects.all():
        x.delete()
    for x in Basket.objects.all().order_by('id').distinct('id'):
        x.delete()
    for x in Hit.objects.all():
        x.delete()
    for x in Scope.objects.all():
        x.delete()
    for x in Occurrence.objects.all():
        x.delete()
    for x in RelationType.objects.all():
        x.delete()

    print('(re)creating initial data')
    Scope.objects.get_or_create(scope="Generic", id=0)
    RelationType.objects.get_or_create(rtype='Generic', role_from='Generic', role_to='Generic', id=0)

    read_stopwords()

    # Create an empty basket.
    Basket.objects.get_or_create(label="")


def erase_data():
    """
    Erase instance data, keep type data.
    """
    Hit.objects.all().delete()
    Basket.objects.all().order_by('id').distinct('id').delete()
    Scope.objects.all().delete()
    Occurrence.objects.all().delete()
    Location.objects.all().delete()
    Document.objects.all().delete()
    Content.objects.all().delete()
    RelatedHit.objects.all().delete()
    RelatedBasket.objects.all().delete()
    RelationType.objects.all().delete()
    Tokengroup.objects.all().delete()


def get_statistics():

    statistics = {}
    statistics['document_count'] = len(Document.objects.all())
    statistics['hit_count'] = len(Hit.objects.all())
    statistics['basket_count'] = len(Basket.objects.all().order_by('id').distinct('id'))
    statistics['occurrence_count'] = len(Occurrence.objects.all())
    statistics['occurrences_found_count'] = len(Occurrence.objects.exclude(hit_in_content='Not Found'))
    statistics['occurrences_not_found_count'] = len(Occurrence.objects.filter(hit_in_content='Not Found'))
    statistics['see_count'] = len(RelatedHit.objects.filter(relationtype__rtype='See'))
    statistics['relation_count'] = len(RelatedBasket.objects.all())
    statistics['seealso_count'] = len(RelatedBasket.objects.filter(relationtype__rtype='SeeAlso'))
    statistics['synonym_count'] = len(RelatedHit.objects.filter(relationtype__rtype='Synonym'))
    statistics['subentry_count'] = len(Hit.objects.filter(name__contains='--'))

    statistics['containment'] = len(RelatedBasket.objects.filter(relationtype__rtype='Containment'))

    statistics['multiple_tokens'] = len(RelatedBasket.objects.filter(relationtype__rtype='MultipleTokens'))

    return statistics


def xslt(kwargs):
    """
    Transforms 'source' into 'result'
    using XSLT 2.0 transformation 'xsl' with Saxon HE 9.5
    """
    command = 'saxon9he-xslt -xsl:%s %s > %s' % (
        kwargs['xsl'],
        kwargs['source'],
        kwargs['result'],
    )
    subprocess.call(command, shell=True)


def xslt_no_ns(kwargs):
    """
    Transforms 'source' into 'result'
    using XSLT 2.0 transformation 'xsl' with Saxon HE 9.5
    """
    command = 'saxon9he-xslt --suppressXsltNamespaceCheck:on -xsl:%s %s > %s' % (
        kwargs['xsl'],
        kwargs['source'],
        kwargs['result'],
    )
    subprocess.call(command, shell=True)


def xslt_live(kwargs):
    """
    Transforms 'source' into 'result'
    using XSLT 2.0 transformation 'xsl' with Saxon HE 9.5
    """

    command = 'saxon9he-xslt -xsl:%s %s ' % (
        kwargs['xsl'],
        kwargs['source'],
    )
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = p.communicate()[0].strip().decode('utf-8')

    return output
