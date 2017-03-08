from django.db.models import Count

from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Ttype
from .serializers import TtypeSerializer, TtypeWithCountsSerializer
from otcore.management.views import DeleteIfUnusedMixin


class AllTypesView(generics.ListCreateAPIView):
    serializer_class = TtypeSerializer

    def get_queryset(self):
        queryset = Ttype.objects.all()
        basket_id = self.request.query_params.get('basket_id', None)
        if basket_id is not None:
            queryset = queryset.filter(baskets__id=basket_id)

        return queryset


class AllTypesWithCountsView(generics.ListAPIView):
    queryset = Ttype.objects.all().annotate(count=Count('baskets'))
    serializer_class = TtypeWithCountsSerializer


class RemoveTypeView(DeleteIfUnusedMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Ttype.objects.all()
    serializer_class = TtypeSerializer
    check_fields = ['baskets']
    detach_field = 'baskets'
