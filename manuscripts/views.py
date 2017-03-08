import os

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from otcore.occurrence.models import Location, Document
from otcore.occurrence.views import DocumentDetailView, LocationDetailView
from otcore.hit.views import get_basket_data
from otcore.hit.models import Basket
from otx_epub.models import Epub

from .serializers import EpubLocationFullSerializer, EpubDocumentSerializer, \
    EpubListSerializer, IndexSerializer, IndexPatternSerializer
from .models import Index, IndexPattern
from .processing import nyu_process_single_basket
from initial.pattern_mapping import pattern_mapping


class EpubDocumentDetailView(DocumentDetailView):
    queryset = Epub.objects.prefetch_related('locations', 'locations__content').all()
    serializer_class = EpubListSerializer

    def list(self, request, *args, **kwargs):
        doc_id = self.kwargs['pk']
            
        locations = Location.objects.filter(document_id=doc_id).select_related(
                    'content', 'document', 'document__epub'
                ).prefetch_related(
                    'occurrences', 'occurrences__basket'
                ).order_by('sequence_number')

        if locations:
            pattern_name = pattern_mapping[os.path.basename(locations[0].document.epub.contents)]
            indexpattern = IndexPattern.objects.get(name=pattern_name)
            data = EpubLocationFullSerializer(locations, many=True, context={ 'indexpattern': indexpattern}).data
        else:
            data = []

        return Response(data)


class EpubDocumentListView(generics.ListAPIView):
    queryset = Epub.objects.order_by('publisher', 'author')
    serializer_class = EpubDocumentSerializer


class EpubLocationView(LocationDetailView):
    queryset = Location.objects.select_related(
            'content',
            'document',
            'document__epub'
        ).prefetch_related(
            'occurrences',
            'occurrences__basket'
        )
    serializer_class = EpubLocationFullSerializer


class IndexURLView(generics.ListAPIView):
   """
   Fetches the associated index by location
   """
   serializer_class = IndexSerializer 

   def get_queryset(self):
        l = Location.objects.filter(id=self.kwargs.get('location_id', None)).select_related(
            'document',
            'document__epub'
        )[0]

        return Index.objects.filter(epub=l.document.epub)


class AutomaticRelationView(APIView):
    """
    Reruns MultipleTokens and Containment on a single basket
    """
    def put(self, request, *args, **kwargs):
        basket_query = Basket.objects.filter(id=self.kwargs['basket_id']).prefetch_related(
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

        nyu_process_single_basket(basket)

        add_types_to_relations = self.request.query_params.get('add_types', False)
        data = get_basket_data(basket, add_types_to_relations=add_types_to_relations)

        return Response(data)


class AllIndexPatternsView(generics.ListAPIView):
    serializer_class = IndexPatternSerializer
    queryset = IndexPattern.objects.all()
