from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from otcore.hit.views import HitSearchView, BasketSearchView
from otcore.hit.models import Hit, Basket
from .serializers import ReviewSerializer, HitListWithReviewSerializer, ReportSerializer, \
    BasketListWithReviewSerializer
from .models import Review, Report
from .reports import generate_csv_report


class SetReviewed(generics.RetrieveUpdateAPIView):
    """
    View that sets the 'reviewed' field on the Review model for a given
    basket.  Expects data in the following format:
        {
            reviewed: SOME_BOOLEN,
            changed: SOME_BOOLEAN
        }
    If the basket in question doesn't currently have an associated review object,
    one will be created.
    """
    lookup_field = 'basket_id'
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    
    def put(self, request, *args, **kwargs):
        data = request.data
        data['reviewer'] = request.user.id
        data['time'] = timezone.now()
        print(data)
       
        try:
            review = self.get_object()
        except Review.DoesNotExist:
            review = Review(basket_id=request.kwargs['basket_id'])

        serializer = self.serializer_class(review, data=data)
        serializer.is_valid()
        review = serializer.save()

        return Response(serializer.data)


class ReviewAllBasketsView(generics.ListAPIView):
    """
    Overriding standard All Baskets view to include Review info
    """
    serializer_class = BasketListWithReviewSerializer
    queryset = Basket.objects.select_related('review', 'review__reviewer').all()


class ReviewBasketSearchView(BasketSearchView):
    """
    Overriding the Basket search view to provide Review info
    """
    serializer_class = BasketListWithReviewSerializer
    queryset = Basket.objects.select_related('review', 'review__reviewer').all()


class ReviewAllHitsView(generics.ListAPIView):
    """
    Overriding standard All Hits view to include Review info
    """
    serializer_class = HitListWithReviewSerializer
    queryset = Hit.objects.all().select_related(
        'scope', 
        'basket__review',
        'basket__review__reviewer').filter(bypass=False)


class ReviewHitSearchView(HitSearchView):
    """
    Overriding Hit search view to include Review info
    """
    serializer_class = HitListWithReviewSerializer 
    queryset = Hit.objects.all().select_related(
        'scope', 
        'basket__review',
        'basket__review__reviewer').filter(bypass=False)


class AllReportsView(generics.ListAPIView):
    """
    All Generated Reports
    """
    serializer_class = ReportSerializer
    queryset = Report.objects.all()


class DeleteReportView(generics.DestroyAPIView):
    """
    Remove Report
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer


class NewReportView(APIView):
    """
    Generates a Report.  Returns serializer report info

    must be sent one of Report.TOPIC_SETS, eg:
        { 'report_type': 'R' }
    """
    def post(self, request, *args, **kwargs):
        report_type = request.data['report_type']

        report = generate_csv_report(report_type)

        return Response(ReportSerializer(report).data)


class AllReportTypesView(APIView):
    """
    Returns all the Report Types
    """
    def get(self, request, *args, **kwargs):
        return Response(Report.TOPIC_SETS)
