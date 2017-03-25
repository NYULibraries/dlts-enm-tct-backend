from collections import Counter

import django_filters
from django.db.models import Q, Count
from django.views.generic.base import TemplateView
from django.core.exceptions import FieldError
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .forms import add_or_create_from_uiselect
from otcore.hit.models import Hit, Basket, Scope
from otcore.hit.serializers import HitSerializer, BasketSerializer, HitListSerializer, \
    HitUpdateSerializer, HitListWithBasketNamesSerializer, HitCreateSerializer, \
    ScopeSerializer, BasketSimpleSerializer, ScopeWithCountsSerializer, BasketSimpleSerializer, \
    BasketListWithCountsSerializer
from otcore.hit.processing import merge_baskets, detach
from otcore.relation.models import RelatedBasket
from otcore.relation.serializers import RelatedBasketSerializer
from otcore.occurrence.models import Occurrence
from otcore.lex.lex_utils import lex_slugify
from otcore.topic.models import Ttype
from otcore.topic.serializers import TtypeSerializer


def get_basket_data(basket, add_types_to_relations=False):
    # NOTE: distinct on individual fields is only possible in postgres

    related_data = []
    for direction in ['source', 'destination']:
        this_basket = 'source' if direction == 'destination' else 'destination'

        # user kwargs dictionary allows us to make dynamic filter calls, changing the filter query
        # depending on whether we're dealing with the source or destination basket
        filter_kwargs = { 'forbidden': False, this_basket: basket}
        related_query = RelatedBasket.objects.filter(**filter_kwargs).select_related('relationtype', direction)

        if add_types_to_relations:
            related_query = related_query.prefetch_related('{}__types'.format(direction))

        related_query = related_query.order_by('id').distinct('id')

        # for r in related_query:
        #    print("{} {} {} {}".format(direction, r.source.id, r.destination.id, r.id))

        # pass direction query into serializer to get properly serializer relation
        related_data_subset = RelatedBasketSerializer(
                related_query,
                many=True,
                direction=direction,
                add_basket_types=add_types_to_relations
        ).data
        related_data = related_data + related_data_subset

    related_data.sort(key=lambda x: x['basket']['display_name'].lower())

    basket_data = BasketSerializer(basket).data
    basket_data['occurs'] = sorted(basket_data['occurs'], key=lambda x: (
        x['location']['document']['author'],
        x['location']['document']['title'],
        x['location']['sequence_number']))

    data = {
        "basket": basket_data,
        "relations": related_data,
    }

    return data


##########################################
# Editorial Interface Views
##########################################


class AllHitsView(generics.ListAPIView):
    serializer_class = HitListSerializer
    queryset = Hit.objects.all().select_related('scope').filter(bypass=False)


class HitFilter(django_filters.rest_framework.FilterSet):
    exclude_basket = django_filters.CharFilter(method='filter_exclude_basket')
    name = django_filters.CharFilter(lookup_expr='icontains')
    exclude_type = django_filters.CharFilter(method='filter_exclude_type')
    ttype = django_filters.CharFilter(name='basket__types__ttype')
    scope = django_filters.CharFilter(name='scope__scope')
    letter = django_filters.CharFilter(method='filter_letter')

    def filter_letter(self, queryset, name, value):
        if value == '#':
            queryset = queryset.exclude(name__regex=r'^[\'\"]?[A-Za-z]')
        elif value is not None:
            queryset = queryset.filter(name__iregex=r'^[\'\"]?{}'.format(value))

        return queryset

    def filter_exclude_type(self, queryset, name, value):
        if value:
            for val in value.split(','):
                queryset = queryset.exclude(basket__types__ttype=val)

        return queryset

    def filter_exclude_basket(self, queryset, name, value):
        if value:
            values = value.split(',')
            queryset = queryset.exclude(basket_id__in=values)

        return queryset

    class Meta:
        model = Hit
        fields = ('name', 'exclude_basket', 'exclude_type', 'ttype', 'scope', 'letter')


class HitSearchView(generics.ListAPIView):

    serializer_class = HitListSerializer
    # authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)
    queryset = Hit.objects.filter(bypass=False).select_related('scope').all()
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = HitFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        response = super(HitSearchView, self).list(request, *args, **kwargs)

        if self.request.query_params.get('as_object', None):
            response.data = {'hits': response.data}

        return response


class HitChangeView(APIView):

    # add_or_create_from_uiselect
    def put(self, request, *args, **kwargs):
        hit = Hit.objects.get(id=self.kwargs['pk'])
        new_name = request.data['name']
        name_changed = hit.name != new_name
        scope = add_or_create_from_uiselect(Scope, 'scope', request.data['scope'])
        if name_changed:
            new_name_slug = lex_slugify(new_name)

            if Hit.objects.filter(slug=new_name_slug, scope=scope).exclude(basket_id=hit.basket_id).exists():
                error = ('Same Or Similar Name Already Exists. '
                         'If you want to merge topics, please use the '
                         '"Merge" button. Otherwise, to help disambiguate, '
                         'consider changing scope.')

                return Response({'name': [error]}, status.HTTP_400_BAD_REQUEST)

            else:
                hit.name = new_name
                hit.slug = new_name_slug

        hit.scope = scope
        hit.bypass = request.data['bypass']

        if request.data['hidden'] != hit.hidden:
            try:
                hit.set_hidden(request.data['hidden'])
            except FieldError as e:
                return Response({'hidden': [str(e)]}, status.HTTP_400_BAD_REQUEST)

        # If hit was newly marked as preferred, call make_preferred() function
        # (which will save the hit)
        # Otherwise, call normal save
        if (not hit.preferred and request.data['preferred']) or (name_changed and hit.preferred):
            hit.make_preferred(force=True, save=False)

        hit.save()
        hit.basket.save() # basket save forces display name to recalculate display_name

        return Response(HitSerializer(hit).data)


class HitUnhideView(APIView):
    def get(self, response, *args, **kwargs):
        hit = Hit.objects.get(id=self.kwargs['pk'])

        try:
            hit.set_hidden(False)
        except FieldError as e:
            return Response({'hidden': [repr(e)]}, status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)


class BasketDetailView(APIView):

    def get(self, request, *args, **kwargs):
        basket_query = Basket.objects.filter(id=self.kwargs['pk']).prefetch_related(
            'topic_hits',
            'topic_hits__scope',
            'occurs',
            'occurs__location',
            'occurs__location__document',
            )

        try:
            basket = basket_query[0]
        except IndexError:
            return Response({"Error": "No Basket Matches that ID"})

        add_types_to_relations = self.request.query_params.get('add_types', False)
        data = get_basket_data(basket, add_types_to_relations=add_types_to_relations)

        return Response(data)

    def delete(self, request, *args, **kwargs):
        try:
            basket = Basket.objects.get(id=self.kwargs['pk'])
        except Basket.DoesNotExist:
            return Response({"Error": "No Basket Matches that ID"})

        basket.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class BasketMergeView(APIView):
    """
    Receives the following post data:
        basket_remaining_id: id of the basket to merge into
        basket_discarded_id: id of the basket to merge from (that will then be deleted)
    Returns the merged basket

    """
    def post(self, request, *args, **kwargs):
        basket_discarded = Basket.objects.get(id=request.data['basket_discarded_id'])
        basket_remaining = Basket.objects.get(id=request.data['basket_remaining_id'])

        merged_basket = merge_baskets(basket_discarded, basket_remaining)

        data = get_basket_data(merged_basket)

        return Response(data)


class BulkMergeByHitView(APIView):
    """
    Receives a list of hit ids as patch data, as the object `hit_ids`
    Merges them all into a single basket, and returns a simplified serialized version of the
    Merged basket
    """
    def patch(self, request, *args, **kwargs):
        hit_ids = self.request.data.get('hit_ids', [])

        hits = list(Hit.objects.filter(id__in=hit_ids))
        basket = hits.pop().basket

        for hit in hits:
            # skip if the hit is already on the merged basket
            if hit.basket == basket:
                continue

            basket = merge_baskets(hit.basket, basket)

        return Response({"basket": basket.id})


class BasketListView(generics.ListAPIView):
    serializer_class = BasketSimpleSerializer
    queryset = Basket.objects.all()


class BasketFilter(django_filters.rest_framework.FilterSet):
    letter = django_filters.CharFilter(method='filter_letter')
    counts = django_filters.CharFilter(method='filter_counts')
    document = django_filters.NumberFilter('occurs__location__document_id')

    def filter_letter(self, queryset, name, value):
        if value == '#':
            queryset = queryset.exclude(display_name__regex=r'^[\'\"]?[A-Za-z]')
        elif value is not None:
            queryset = queryset.filter(display_name__iregex=r'^[\'\"]?{}'.format(value))

        return queryset

    def filter_counts(self, queryset, name, value):
        if value:
            queryset = queryset.annotate(occurrence_counts=Count('occurs'))

        return queryset

    class Meta:
        model = Basket
        fields = ('letter', 'document')


class BasketSearchView(generics.ListAPIView):
    serializer_class = BasketSimpleSerializer
    queryset = Basket.objects.all()
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = BasketFilter

    def get_serializer_class(self, *args, **kwargs):
        if self.request.query_params.get('counts', False):
            return BasketListWithCountsSerializer
        else:
            return BasketSimpleSerializer


class AddHit_Main(APIView):

    """
    Submit a name. The following logic is used
    Does the basket have an exact name match?
        - YES: Do nothing
        - NO: Does a slug match exist?
            - YES: Is there a slug match on the current basket?
                - YES: Does the slug exist elsewhere?
                    - YES: Add a new hit and take scope from existing hits on basket
                           that share the same slug
                    - NO: Add new hit
                - NO: Disambiguate or Merge
            - NO: Add new hit
    """
    def post(self, request, *args, **kwargs):
        newHitName = self.request.data['hit_name']

        # Check for Bypassed
        if Hit.objects.filter(name=newHitName, bypass=True).exists():
            return Response({'error': 'Name has been bypassed.'}, status.HTTP_400_BAD_REQUEST)

        slug = lex_slugify(newHitName)

        basket = Basket.objects.get(id=self.request.data['basket_id'])
        basket_hits = basket.topic_hits.all()

        # If the current name is already on the basket, do nothing
        basket_names = [hit.name for hit in basket_hits]
        if newHitName in basket_names:
            return Response({'editorialAction': 'nothing'})

        hits_with_slug = Hit.objects.filter(slug=slug)

        # Is there a slug match?
        if hits_with_slug:
            # is the slug on the current basket?
            basket_slugs = [hit.slug for hit in basket_hits]
            if slug in basket_slugs:
                matching_hits = [h for h in basket_hits if h.slug == slug]
                # is the slug elsewhere?
                if len(hits_with_slug) > len(matching_hits):
                    hit = Hit.objects.create(name=newHitName,
                                             basket=basket,
                                             scope=matching_hits[0].scope)
                else:
                    hit = Hit.objects.create(name=newHitName, basket=basket)

                hit.save()
                return Response({'editorialAction': 'addHit',
                                 'hit': HitSerializer(hit).data,})

            else:
                return Response({'editorialAction': 'conflictExists',
                                 'hits': HitListWithBasketNamesSerializer(
                                     hits_with_slug,
                                     many=True
                                 ).data})

        else:
            hit = Hit.objects.create(name=newHitName, basket=basket)
            hit.save()
            return Response({'editorialAction': 'addHit',
                             'hit': HitSerializer(hit).data,})



class AddHitWithExistingSlug(APIView):

    def post(self, request, *args, **kwargs):

        newHitName = self.request.data['hit_name']
        basket = Basket.objects.get(id=self.request.data['basket_id'])

        hit = Hit.objects.create(name=newHitName, basket=basket)
        hit.save()
        return Response(HitSerializer(hit).data)


class UpdateHitScopesView(APIView):
    """
    Get a list of Hits
    If the Scope id = -1, this means a new scope with that "scope" has to be created
    then save all the Hits
    """

    def patch(self, request, *args, **kwargs):
        # Update scopes of already existing Hits
        # create the scope first, if it doesn't exist
        # The first hit is skipped, because it is always the new hit
        for hit_data in request.data['hits'][1:]:
            hit = Hit.objects.get(id=hit_data['id'])

            self.hit_scope_update(hit, hit_data['scope'])

        # Create the new hit, including scope
        # create the scope if it doesn't exist
        new_hit_data = request.data['hits'][0]
        hit = Hit(name=new_hit_data['name'], basket_id=new_hit_data['basket']['id'])

        hit = self.hit_scope_update(hit, new_hit_data['scope'])

        return Response(HitSerializer(hit).data)

    def hit_scope_update(self, hit, scope_data):
        if scope_data['id'] == -1:
            scope = Scope(scope=scope_data['scope'])
            scope.save()

            hit.scope = scope
            hit.save()

        else:
            hit.scope_id = scope_data['id']
            hit.save()

        return hit


class CreateHitView(generics.CreateAPIView):

    serializer_class = HitCreateSerializer
    queryset = Hit.objects.all()


class HitDeleteView(generics.DestroyAPIView):
    queryset = Hit.objects.all()
    serializer_class = HitUpdateSerializer


class ScopeListCreateView(generics.ListCreateAPIView):
    queryset = Scope.objects.all()
    serializer_class = ScopeSerializer


class ScopeListWithCountsView(generics.ListCreateAPIView):
    queryset = Scope.objects.annotate(count=Count('hits'))
    serializer_class = ScopeWithCountsSerializer


class SingleScopeView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Scope.objects.all()
    serializer_class = ScopeSerializer


class DetachView(APIView):
    def post(self, request, *args, **kwargs):
        old_basket = Basket.objects.get(id=request.data['basket_id'])
        hit = Hit.objects.get(id=request.data['hit_id'])

        corrected_old_basket, _ = detach(hit, old_basket, request.data['split_data'])

        data = get_basket_data(corrected_old_basket)

        return Response(data)


class AddTypetoBasketView(APIView):

    def patch(self, request, *args, **kwargs):
        basket = Basket.objects.get(id=self.kwargs['pk'])

        ttype = add_or_create_from_uiselect(Ttype, 'ttype', request.data)
        basket.types.add(ttype)

        return Response(TtypeSerializer(ttype).data)


class SetHitBypassView(generics.UpdateAPIView):
    """
    Sets the bypass value of a given hit.
    Expects to receive a `bypass_val` patch data object, set to True or False
    """
    serializer_class = HitSerializer
    queryset = Hit.objects.all()

    def patch(self, request, *args, **kwargs):
        hit = self.get_object()

        bypass_val = request.data.get('bypass_val', None)
        hit.set_bypass(bypass_val)

        return Response(status=status.HTTP_204_NO_CONTENT)


class BaseBulkBypassView(APIView):
    """
    Sets the bypass of a list of hits to bypass_val by calling set_bypass
    Expects to recieve a `hits` patch data object, with a list of hit ids to be bypassed
    """
    bypass_val = None

    def patch(self, request, *args, **kwargs):
        assert self.bypass_val is not None, (
            "'%s' must set the `bypass_val` variable."
            % self.__class__.__name__
        )

        hit_ids = request.data.get('hits', [])

        hits = Hit.objects.filter(id__in=hit_ids)

        for hit in hits:
            hit.set_bypass(self.bypass_val)

        return Response(status=status.HTTP_204_NO_CONTENT)


class BulkBypassView(BaseBulkBypassView):
    bypass_val = True


class BulkUnbypassView(BaseBulkBypassView):
    bypass_val = False


class BypassedHitsView(generics.ListAPIView):
    """
    Returns a list of all bypassed hits
    """
    serializer_class = HitListSerializer
    queryset = Hit.objects.all().select_related('scope').filter(bypass=True)


class BypassedHitsView(generics.ListAPIView):
    """
    Returns a list of all bypassed hits
    """
    serializer_class = HitListSerializer
    queryset = Hit.objects.all().select_related('scope').filter(bypass=True)


class NewBasketView(APIView):
    """
    API Endpoint for creating a basket from scratch.
    Takes a topic name.  If that name (or its slug equivalent) already exists
    It returns an error.  Otherwise, it creates the corresponding hit and basket.
    """
    def post(self, request, *args, **kwargs):
        hit_name = request.data['hit']

        slug = lex_slugify(hit_name)

        if Hit.objects.filter(slug=slug).exists():
            return Response({'error': 'Same or Similiar Topic Name Already Exists'}, status.HTTP_400_BAD_REQUEST)

        else:
            hit = Hit.objects.create(name=hit_name)
            hit.create_basket_if_needed()
            basket = hit.basket

            return Response(BasketSimpleSerializer(basket).data, status.HTTP_201_CREATED)
