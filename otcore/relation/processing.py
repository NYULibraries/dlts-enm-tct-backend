from django.db.models import Q, Count
from otcore.hit.models import Hit, Basket
from otcore.relation.models import RelationType, RelatedBasket
from otcore.topic.models import Tokengroup
from otcore.settings import setting



def get_rtypes():
    containment, _ = RelationType.objects.get_or_create(rtype="Containment",
        defaults = {
            'role_from': 'contained by',
            'role_to': 'contains',
            'symmetrical': False
        }
    )

    multipletokens, _ = RelationType.objects.get_or_create(rtype="MultipleTokens",
        defaults = {
            'role_from': 'Multiple Tokens with',
            'role_to': 'Multiple Tokens with',
        }
    )

    return {
        'containment': containment,
        'multipletokens': multipletokens
    }


def global_containment():
    """
    Runs the containment rule for every hit.
    """
    rtypes = get_rtypes()

    counter=0
    all_slugs = Hit.objects.order_by('slug').distinct('slug').values_list('slug', flat=True)
    slug_sets = [(frozenset(slug.split('-')), slug) for slug in all_slugs]
    slug_sets = sorted(list(slug_sets), key=lambda x: len(x[0]))

    while len(slug_sets) > 0:
        single_hit_containment(slug_sets[0], slug_sets[1:], rtypes)
        slug_sets = slug_sets[1:]
        counter += 1


def process_single_basket(basket):
    """
    Runs containment and multipletokens on a on a single basket
    """
    rtypes = get_rtypes()

    # Containment
    all_slugs = Hit.objects.order_by('slug').distinct('slug').values_list('slug', flat=True)
    slug_sets = [(frozenset(slug.split('-')), slug) for slug in all_slugs]

    basket_slugs = basket.topic_hits.order_by('slug').distinct('slug').values_list('slug', flat=True)

    for slug in basket_slugs:
        slug_set = (frozenset(slug.split('-')), slug)
        longer_slugs = [s for s in slug_sets if len(slug_set[0]) < len(s[0])]
        single_hit_containment(slug_set, longer_slugs, rtypes)

        shorter_slugs = [s for s in slug_sets if len(slug_set[0]) > len(s[0])]
        reverse_containment(slug_set, shorter_slugs, rtypes)

    # Multiple Tokens
    basket.local_tokengroup()
    for tokengroup in basket.tokengroups.all():
        single_tokengroup_check(tokengroup, rtypes)


def single_hit_containment(slug_set, slug_sets, rtypes):
    """
    runs containment on a single slug.  Assumes that the slug being passed in is
    shorter than the remaining slugs.  If it's longer, run the `reverse_containment` instead
    """
    results = [s[1] for s in slug_sets if slug_set[0] < s[0]]

    for result in results:
        source_hits = Hit.objects.filter(slug=slug_set[1], basket__isnull=False)
        result_hits = Hit.objects.filter(slug=result, basket__isnull=False)

        for source_hit in source_hits:
            for result_hit in result_hits:
                if source_hit.basket != result_hit.basket and not RelatedBasket.objects.filter(source=source_hit.basket, destination=result_hit.basket).exists():
                    RelatedBasket.objects.create(
                        relationtype=rtypes['containment'],
                        source=source_hit.basket,
                        destination=result_hit.basket
                    )


def reverse_containment(slug_set, slug_sets, rtypes):
    results = [s[1] for s in slug_sets if s[0] < slug_set[0]]

    for result in results:
        source_hits = Hit.objects.filter(slug=slug_set[1], basket__isnull=False)
        result_hits = Hit.objects.filter(slug=result, basket__isnull=False)

        for source_hit in source_hits:
            for result_hit in result_hits:
                if source_hit.basket != result_hit.basket and not RelatedBasket.objects.filter(source=result_hit.basket, destination=source_hit.basket).exists():
                    RelatedBasket.objects.create(
                        relationtype=rtypes['containment'],
                        source=result_hit.basket,
                        destination=source_hit.basket
                    )


def one_containment(name):
    """
    Runs the containment rule for one hit.
    """
    all_slugs = Hit.objects.order_by('slug').distinct('slug').values_list('slug', flat=True)
    slug_sets = [(frozenset(slug.split('-')), slug) for slug in all_slugs]

    rtypes = get_rtypes()

    hits = Hit.objects.filter(name=name)
    slug = hits[0].slug

    slug_set = (frozenset(slug.split('-')), slug)
    longer_slugs = [s for s in slug_sets if len(slug_set[0]) < len(s[0])]
    single_hit_containment(slug_set, longer_slugs, rtypes)

    shorter_slugs = [s for s in slug_sets if len(slug_set[0]) > len(s[0])]
    reverse_containment(slug_set, shorter_slugs, rtypes)


def global_tokengroups():
    """
    Create token groups for all baskets.
    """
    print('Processing: Global Token Groups')
    counter = 0
    baskets_number = Basket.objects.count()
    for basket in Basket.objects.all().order_by('id').distinct('id'):
        counter += 1
        print('TOKENGROUPS: %s of %s' % (counter, baskets_number))
        basket.local_tokengroup()


def global_multiple_tokens():
    """
    Runs multipletoken rule on all baskets
    """
    rtypes = get_rtypes()

    counter=0
    total=Tokengroup.objects.annotate(c=Count('basket')).filter(c__gt=1).count()
    for tokengroup in Tokengroup.objects.annotate(c=Count('basket')).filter(c__gt=1):
        print("Multiple Tokens {} of {}".format(counter, total))
        counter += 1

        single_tokengroup_check(tokengroup, rtypes)


def single_tokengroup_check(tokengroup, rtypes):
    """
    Does a multipletoken check on a single tokengropu
    """
    baskets = list(tokengroup.basket_set.all())

    while len(baskets) > 1:
        source_basket = baskets.pop()

        for dest_basket in baskets:
            if not RelatedBasket.objects.filter(source=source_basket, destination=dest_basket).exists() and not RelatedBasket.objects.filter(source=dest_basket, destination=source_basket).exists():
                RelatedBasket.objects.create(
                    relationtype=rtypes['multipletokens'],
                    source=source_basket,
                    destination=dest_basket
                )


def alt_global_multiple_tokens():
    """
    Creates MultipleToken Relations without using TokenGroups
    """
    rtypes = get_rtypes()

    hits = Hit.objects.all()
    slug_sets = [(frozenset(hit.slug.split('-')), hit) for hit in hits if len(frozenset(hit.slug.split('-'))) >= setting('MULTIPLE_RELATIONS_COUNT')]

    counter=0
    total=len(slug_sets)
    while len(slug_sets) > 1:
        counter += 1
        print("Multiple Tokens {} of {}".format(counter, total))

        alt_single_set_multiple_tokens(slug_sets[0], slug_sets[1:], rtypes)
        slug_sets = slug_sets[1:]


def alt_single_set_multiple_tokens(slug_set, slug_sets, rtypes):
    """
    Check for multiple token relations on a single hit/slug_set pair
    """
    intersections = [s for s in slug_sets if len(s[0].intersection(slug_set[0])) >= setting('MULTIPLE_RELATIONS_COUNT')]

    for hit_set in intersections:
        hit1 = slug_set[1]
        hit2 = hit_set[1]

        if hit1.basket != hit2.basket and \
                not RelatedBasket.objects.filter(source=hit1.basket, destination=hit2.basket).exists() and \
                not RelatedBasket.objects.filter(source=hit2.basket, destination=hit1.basket).exists():
            RelatedBasket.objects.create(
                relationtype=rtypes['multipletokens'],
                source=hit1.basket,
                destination=hit2.basket
            )
