from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics

from .models import Weblink
from .serializers import WeblinkSerializer
from otcore.hit.models import Basket
from otcore.management.views import DeleteIfUnusedMixin


class AddWeblinkView(APIView):

    def post(self, request, *args, **kwargs):
        basket = Basket.objects.get(id=request.data['basket_id'])

        weblink, _ = Weblink.objects.get_or_create(url=request.data['weblink']['url'], defaults={'content': request.data['weblink']['content']})

        basket.weblinks.add(weblink)

        return Response(WeblinkSerializer(weblink).data)


class SingleWeblinkView(DeleteIfUnusedMixin, generics.RetrieveUpdateDestroyAPIView):
    check_fields = ['baskets']
    detach_field = 'baskets'
    queryset = Weblink.objects.all()
    serializer_class = WeblinkSerializer


class ListWeblinkView(generics.ListAPIView):
    serializer_class = WeblinkSerializer

    def get_queryset(self):
        queryset = Weblink.objects.all()
        basket_id = self.request.query_params.get('basket_id', None)
        if basket_id is not None:
            queryset = queryset.filter(baskets__id=basket_id)

        return queryset
