from otcore.hit.processing import BasketTransformer
from .serializers import NYUBasketSerializer


class NYUBasketTransformer(BasketTransformer):
    basket_serializer = NYUBasketSerializer
