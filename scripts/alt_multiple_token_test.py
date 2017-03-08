import time

from otcore.relation.processing import alt_global_multiple_tokens
from otcore.relation.models import RelatedBasket, RelationType


def run():
    """
    Deletes all Tokengroups and MultipleToken relations.  
    Reruns Tokengropus and MultipleTokens, for timing purposes
    """
    multipletokens = RelationType.objects.get(rtype="MultipleTokens")

    RelatedBasket.objects.filter(relationtype=multipletokens).delete()

    start = time.time()

    alt_global_multiple_tokens()

    end = time.time()

    print("total time: {}".format(end-start))
    print("total multipletokens created: {}".format(RelatedBasket.objects.filter(relationtype=multipletokens).count()))
