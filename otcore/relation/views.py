from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from otcore.topic.models import Tokengroup
from .models import RelatedBasket, RelationType
from .serializers import RelatedBasketSimpleSerializer, RelationTypeSerializer, \
    RelatedBasketSerializer, RelationTypeWithCountsSerializer
from .processing import global_containment, global_tokengroups, global_multiple_tokens


##########################################
# Editorial Interface Views
##########################################


class UpdateRelationView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RelatedBasket.objects.all()
    serializer_class = RelatedBasketSerializer

    def perform_destroy(self, instance):
        if instance.forbidden:
            instance.delete()
        else:
            instance.check_delete()

    def put(self, request, *args, **kwargs):
        relation = self.get_object()

        relation.source_id = request.data['source']
        relation.destination_id = request.data['destination']
        relation.relationtype_id = request.data['relationtype']
        
        if request.data.get('forbidden', None) is not None:
            relation.forbidden = request.data['forbidden']

        relation.save()

        return Response(RelatedBasketSerializer(relation, direction=request.data['direction']).data)
       

class BulkRelationDeleteView(APIView):
    def patch(self, request, *args, **kwargs):
        relations = RelatedBasket.objects.filter(id__in=request.data['relation_ids'])

        relations.check_delete();

        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateDefaultRelatedBasketView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        # origin, _ = Origin.objects.get_or_create(generated_by="Editorial Interface")

        related_basket, created = RelatedBasket.objects.get_or_create(
            source_id=request.data['source'],
            destination_id=request.data['destination'],
        )

        # related_basket.origins.add(origin)

        if not created:
            if not related_basket.forbidden:
                related_basket.forbidden = False
                related_basket.save()
            else:
                return Response({'error': 'Relation Already on Topic'})

        return Response(RelatedBasketSerializer(
            related_basket, 
            direction='destination', 
            add_basket_types=True).data)


class RelationTypesAllView(generics.ListAPIView):
    serializer_class = RelationTypeSerializer
    queryset = RelationType.objects.all()


class CreateFullRelatedBasketView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):

        related_basket, created = RelatedBasket.objects.get_or_create(
            source_id=request.data['source'],
            destination_id=request.data['destination'],
            relationtype_id=request.data['relationtype'],
        )

        if not created:
            if not related_basket.forbidden:
                related_basket.forbidden = False
                related_basket.save()
            else:
                return Response({'error': 'Relation Already on Topic'})

        direction = request.data['direction']
        data = RelatedBasketSerializer(related_basket, direction=direction).data

        return Response(data)


class RelationTypeCreateView(generics.CreateAPIView):
    serializer_class = RelationTypeSerializer
    queryset = RelationType.objects.all()


class RelationTypeUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RelationTypeSerializer
    queryset = RelationType.objects.all()


class RelationTypeWithCountsView(generics.ListAPIView):
    serializer_class = RelationTypeWithCountsSerializer
    queryset = RelationType.objects.annotate(count=Count('related_baskets'))


class ForbiddenRelationsByBasketView(APIView):
    def get(self, request, *args, **kwargs):
        basket_id = kwargs['basket_id']

        sources = RelatedBasket.objects.filter(forbidden=True, source_id=basket_id)
        source_data = RelatedBasketSerializer(sources, many=True, direction='destination').data

        destinations = RelatedBasket.objects.filter(forbidden=True, destination_id=basket_id)
        destination_data = RelatedBasketSerializer(destinations, many=True, direction='source').data

        return Response(source_data + destination_data)
