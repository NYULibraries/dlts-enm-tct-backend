from django.views.generic import ListView, DetailView
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Document, Location, Occurrence
from .serializers import DocumentListSerializer, DocumentDetailSerializer, \
        LocationFullSerializer, OccurrenceFromLocationSerializer, OccurrenceUpdateSerializer, \
        OccurrenceSerializer
from .processing import create_occurrence_rings
from otcore.hit.forms import add_or_create_from_uiselect
from otcore.hit.models import Hit
from otcore.lex.lex_utils import lex_slugify


#  API VIEWS
class DocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentListSerializer


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """
    Data for the document detail page
    If `withOccurrences=True` is passed as a query_param, then it serializers
    all content and occurrences, allowing the entire document to be reconstructed.
    Otherwise, gives a list of locations to link to location detail pages
    """
    queryset = Document.objects.prefetch_related('locations', 'locations__content').all()
    serializer_class = DocumentDetailSerializer

    def get(self, request, *args, **kwargs):
        if self.request.query_params.get('withOccurrences', False):
            return self.list(request, *args, **kwargs)
        else:
            return super(DocumentDetailView, self).get(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        doc_id = self.kwargs['pk']
            
        locations = Location.objects.filter(document_id=doc_id).select_related(
                    'content', 'document'
                ).prefetch_related(
                    'occurrences', 'occurrences__basket'
                ).order_by('sequence_number')

        data = LocationFullSerializer(locations, many=True).data

        return Response(data)


class LocationDetailView(generics.RetrieveAPIView):
    """
    Gets location and its associated content and occurrences
    If `allFromDoc` is set, it gets the full list from the current document instead
    """
    serializer_class = LocationFullSerializer
    queryset = Location.objects.select_related(
        'content',
        'document'
    ).prefetch_related(
        'occurrences',
        'occurrences__basket'
    )

    def get_serializer(self, *args, **kwargs):
        kwargs['location_controls'] = True
        return super(LocationDetailView, self).get_serializer(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.request.query_params.get('allFromDoc', False):
            return self.list(request, *args, **kwargs)
        else:
            return super(LocationDetailView, self).get(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        doc_id = Location.objects.get(id=self.kwargs['pk']).document_id

        queryset = self.queryset.filter(document_id=doc_id).order_by('sequence_number')

        data = self.serializer_class(queryset, many=True).data

        return Response(data)


class OccurrenceNewView(APIView):
    """
    Creates a new occurrence.  Only returns the basket display_name and ids: expected to be 
    used on a location view, rather than a basket view
    """
    def post(self, request, *args, **kwargs):
        occurrence = Occurrence.objects.create(
            location_id=request.data['location_id'],
            basket_id=request.data['basket_id']
        )

        return Response(OccurrenceFromLocationSerializer(occurrence).data)


class OccurrenceAlterView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceUpdateSerializer


class OccurrenceNewWithHitView(APIView):
    """
    Given a Hit name and a location ID, creates the hit (if necessary)
    and creates an Occurrence at the given location.

    Checks for existence of name and slug equivalents.  If there is no
    equivalent, it simply creates the hit.  If only one corresponding possible
    basket exists, that is set as the basket.  If there's ambiguity or conflict, 
    the view returns an error
    """

    def post(self, request, *args, **kwargs):
        hit_name = request.data['hit_name']
        slug = lex_slugify(hit_name)
        error_msg = (
            'Multiple Topics match that name.  Please use the above '
            'button to select the appropriate topic from a list.'
        )

        if Hit.objects.filter(slug=slug).exists:
            name_match_count = Hit.objects.filter(name=hit_name).count()

            if name_match_count > 1:
                return Response({'error': error_msg}, status.HTTP_400_BAD_REQUEST)

            elif name_match_count == 1:
                hit = Hit.objects.get(name=hit_name)
                basket_id = hit.basket_id

            else:
                basket_ids = Hit.objects.filter(slug=slug).values_list('basket_id', flat=True)

                if len(basket_ids) > 1:
                    return Response({'error': error_msg}, status.HTTP_400_BAD_REQUEST)

                elif len(basket_ids) == 1:
                    basket_id = basket_ids[0]

                else:
                    # It's possible to have a slug equivalent but no corresponding baskets
                    # If the slug equivalent is a bypassed name
                    hit = Hit.objects.create(name=hit_name)
                    hit.create_basket_if_needed()
                    basket_id = hit.basket_id

        else:
            hit = Hit.objects.create(name=hit_name)
            hit.create_basket_if_needed()
            basket_id = hit.basket_id
            

        occurrence = Occurrence.objects.create(
            location_id=request.data['location_id'],
            basket_id=basket_id
        )

        return Response(OccurrenceFromLocationSerializer(occurrence).data)


class OccurrenceFromUISelectView(APIView):
    """
    Accepts data in the following form:
    {
        'location_id': LOCATION_ID,
        'hit': {
            'name': 'SOME_STRING'
            'id': BASKET_ID
        }
    }
    If `hit.id` is a positive integer, create an occurrence linking the basket and location.
    If `hit.id` is -1, then create a hit with that name, create the requisite basket
    and then create the matching occurrence
    """
    def post(self, request, *args, **kwargs):
        hit = add_or_create_from_uiselect(Hit, 'name', request.data['hit'])
        hit.create_basket_if_needed()

        occurrence, _ = Occurrence.objects.get_or_create(
            basket=hit.basket, location_id=request.data['location_id']
        )

        serializer = OccurrenceFromLocationSerializer(occurrence)

        return Response(serializer.data)


class OccurrenceNewOnBasketView(APIView):
    def post(self, request, *args, **kwargs):
        occurrence, _ = Occurrence.objects.get_or_create(
            location_id=request.data['location_id'],
            basket_id=request.data['basket_id']
        )

        return Response(OccurrenceSerializer(occurrence).data)


class BaseExtractorView(generics.GenericAPIView):
    """
    Base class for creating Extraction views

    As it expects new Document objects to be created, it defaults
    to using POST (the RESTful standard for new objects/create views)

    Expects the source to be extracted to match the `data_source_key`,
    which defaults to source.  Returns the newly created document object
    """

    extractor_class = None
    data_source_key = 'source'
    serializer_class = DocumentListSerializer

    def get_extractor_class(self, request):
        """
        Defaults to using self.extractor_class, but can be
        overridden to provide customized behavior
        """
        assert self.extractor_class is not None, (
            "'%s' should either include a `extractor_class` attribute, "
            "or override the `get_extractor_class()` method."
            % self.__class__.__name__
        )

        return self.extractor_class

    def process_source(self, source):
        """
        Optional function to pre-process source, if work must be done
        before the source is run through the extractor
        """
        return source

    def load_source(self, request):
        """
        Gets the source from the posted data
        """
        try:
            source = self.process_source(request.data[self.data_source_key])
        except KeyError:
            msg = (
                "This endpoints requires a source to be sent with the json "
                "key {}.  Expected key was missing from request"
                .format(self.data_source_key)
            )
            return Response({"error": msg}, status.HTTP_400_BAD_REQUEST)

        return source

    def post(self, request, *args, **kwargs):

        source = self.load_source(request)

        extractor_class = self.get_extractor_class(source)

        extractor = extractor_class(source)
        extractor.extract_all()

        serializer = self.get_serializer(extractor.document)

        return Response(serializer.data)


class BaseBulkExtractorView(BaseExtractorView):
    """
    Base class for Bulk Extracting Documents
    """
    data_source_key = 'sources'

    def post(self, request, *args, **kwargs):
        extractor_class = self.get_extractor_class(request)

        sources = self.load_source(request)

        extractor_class.bulk_extract(sources)

        return Response(status.HTTP_204_NO_CONTENT)
        
        
