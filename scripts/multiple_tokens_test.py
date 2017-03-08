import time

from otcore.relation.processing import global_tokengroups, global_multiple_tokens
from otcore.relation.models import RelatedBasket, RelationType
from otcore.topic.models import Tokengroup


def run():
    """
    Deletes all Tokengroups and MultipleToken relations.  
    Reruns Tokengropus and MultipleTokens, for timing purposes
    """
    multipletokens = RelationType.objects.get(rtype="MultipleTokens")

    RelatedBasket.objects.filter(relationtype=multipletokens).delete()
    Tokengroup.objects.all().delete()

    start = time.time()

    global_tokengroups()

    mid = time.time()

    global_multiple_tokens()

    end = time.time()

    print("total time: {}".format(end-start))
    print("creating tokengroups: {}".format(mid-start))
    print("create multipletoken relations: {}".format(end-mid))
    print("total multipletokens created: {}".format(RelatedBasket.objects.filter(relationtype=multipletokens).count()))
