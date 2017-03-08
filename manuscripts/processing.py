from django.db.models import Count

from otcore.relation.models import RelationType, RelatedBasket
from otcore.relation.processing import single_hit_containment, reverse_containment
from otcore.hit.models import Hit, Basket
from otcore.topic.models import Tokengroup
from otcore.settings import setting


def write_multiple_tokens(filename):
    mt = RelationType.objects.get(rtype='MultipleTokens')

    with open(filename, 'w') as f:
        for r in RelatedBasket.objects.filter(relationtype=mt).select_related('source', 'destination'):
            f.write('{}|{}\n'.format(r.source.display_name, r.destination.display_name))


def get_rtypes():
    containment, _ = RelationType.objects.get_or_create(rtype="Containment",
        defaults = {
            'role_from': 'contained by',
            'role_to': 'contains',
            'symmetrical': False
        }
    )

    subentry, _ = RelationType.objects.get_or_create(rtype="Subentry",
        defaults = {
            'role_from': 'Main Entry of',
            'role_to': 'Subentry of',
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
        'subentry': subentry,
        'multipletokens': multipletokens
    }


def nyu_process_single_basket(basket, run_containment=True, run_multipletokens=True):
    """
    Runs containment and multipletokens on a on a single basket
    """
    rtypes = get_rtypes()

    if run_containment:
        all_slugs = Hit.objects.order_by('slug').distinct('slug').values_list('slug', flat=True)
        slug_sets = [(frozenset(slug.split('-')), slug) for slug in all_slugs]

        basket_slugs = basket.topic_hits.order_by('slug').distinct('slug').values_list('slug', flat=True)

        for slug in basket_slugs:
            slug_set = (frozenset(slug.split('-')), slug)
            longer_slugs = [s for s in slug_sets if len(slug_set[0]) < len(s[0])]
            single_hit_containment(slug_set, longer_slugs, rtypes)

            shorter_slugs = [s for s in slug_sets if len(slug_set[0]) > len(s[0])]
            reverse_containment(slug_set, shorter_slugs, rtypes)

    if run_multipletokens:
        hits = Hit.objects.all()
        slug_sets = [(frozenset(hit.slug.split('-')), hit) for hit in hits if len(frozenset(hit.slug.split('-'))) >= setting('MULTIPLE_RELATIONS_COUNT')]


        for hit in basket.topic_hits.all():
            slug_set = (frozenset(hit.slug.split('-')), hit)
            nyu_single_set_multiple_tokens(slug_set, slug_sets, rtypes)


def nyu_global_multiple_tokens():
    """
    Runs multipletoken rule on all baskets
    """
    rtypes = get_rtypes()

    hits = Hit.objects.all()
    slug_sets = [(frozenset(hit.slug.split('-')), hit) for hit in hits if len(frozenset(hit.slug.split('-'))) >= setting('MULTIPLE_RELATIONS_COUNT')]

    while len(slug_sets) > 1:
        nyu_single_set_multiple_tokens(slug_sets[0], slug_sets[1:], rtypes)
        slug_sets = slug_sets[1:]


def nyu_single_set_multiple_tokens(slug_set, slug_sets, rtypes):
    """
    Check for multiple token relations on a single hit/slug_set pair.  If the two baskets share
    a common main entry, the cuttoff for multiple relations is actually:
       number-of-slugs-in-main-entry + 1
    """
    intersections = [s for s in slug_sets if len(s[0].intersection(slug_set[0])) >= setting('MULTIPLE_RELATIONS_COUNT')]

    for hit_set in intersections:
        hit1 = slug_set[1]
        hit2 = hit_set[1]

        if hit1.basket != hit2.basket and \
                not RelatedBasket.objects.filter(source=hit1.basket, destination=hit2.basket).exists() and \
                not RelatedBasket.objects.filter(source=hit2.basket, destination=hit1.basket).exists():

            shared_main = get_shared_main_entry(hit1.basket, hit2.basket, rtypes=rtypes)
            # print("{} | {} | {}".format(shared_main, hit1, hit2))

            # Skip creating relation if the number of shared slugs is less than main_slugs + 1
            if shared_main is not None:
                main_tokens = [set(hit.slug.split('-')) for hit in shared_main.topic_hits.all()]
                # get the slug of the name in common with the subentries
                try:
                    shared_tokens = sorted([tokens for tokens in main_tokens
                                if tokens < slug_set[0] and tokens < hit_set[0]
                                ], key=lambda x: len(x), reverse=True)[0]
                except IndexError:
                    # means that this combination of hits aren't those shared by this topic.
                    # Move on to the next set
                    print("SKIPPING: {} | {} | {}".format(shared_main, hit1, hit2))
                    continue


                main_token_count = len(shared_tokens)

                if len(slug_set[0].intersection(hit_set[0])) <= main_token_count:
                    continue

            RelatedBasket.objects.create(
                relationtype=rtypes['multipletokens'],
                source=hit1.basket,
                destination=hit2.basket
            )


def get_shared_main_entry(basket1, basket2, rtypes=None):
    """
    Takes two baskets, and checks to see if they are both subentries of the same main entry
    """
    if rtypes is None:
        rtypes = get_rtypes()

    first_mains = get_main_entry(basket1, rtypes=rtypes)
    second_mains = get_main_entry(basket2, rtypes=rtypes)

    if first_mains is not None and second_mains is not None:
        for first in first_mains:
            for second in second_mains:
                if first == second:  
                    return first


def get_main_entry(basket, rtypes=None):
    """
    Given a basket, gets the main entry if it's a subentry.  
    Otherwise, returns none.
    Note that a merged basked COULD be a subentry of two different topics.  Therefore, this function
    returns a list of main topics, rather than a single main
    """ 
    if rtypes is None:
        rtypes = get_rtypes()

    relations = RelatedBasket.objects.filter(destination=basket, relationtype=rtypes['subentry'])

    if len(relations) == 0:
        return None
    else:
        baskets = [relation.source for relation in relations]

        return baskets


def delete_multiple_tokens_from_shared_subentries():
    """
    Utility function for deleting MultipleToken relationships only when
    two topics share the same main entry
    """
    rtypes = get_rtypes()
    for relation in RelatedBasket.objects.filter(relationtype=rtypes['multipletokens']):
        if get_shared_main_entry(relation.source, relation.destination) is not None:
            relation.delete()
