from rest_framework import serializers
from otcore.relation.models import RelationType, RelatedHit, RelatedBasket


class RelationTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelationType
        fields = ('id', 'rtype', 'role_from', 'role_to', 'symmetrical')


class RelationTypeWithCountsSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()

    class Meta:
        model = RelationType
        fields = ('id', 'rtype', 'role_from', 'role_to', 'symmetrical', 'count')


class RelatedHitSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelatedHit
        fields = ('id', 'relationtype', 'origins', 'forbidden', 'source', 'destination', )


class RelatedBasketSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatedBasket
        fields = ('forbidden',)


class NewRelatedBasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatedBasket
        fields = ('relationtype', 'source', 'destination')


class RelatedBasketSerializer(serializers.ModelSerializer):

    """
    Relations with Hit, Basket model.

    """
    def __init__(self, *args, **kwargs):
        self.direction = kwargs.pop('direction', None)
        self.add_basket_types = kwargs.pop('add_basket_types', False)

        assert self.direction == 'destination' or self.direction == 'source', (
            "You must pass the `direction` kwarg into the RelatedBasketSerializer, "
            "and it must be set to either 'destination' or 'source'."
        )

        super(RelatedBasketSerializer, self).__init__(*args, **kwargs)

    basket = serializers.SerializerMethodField(method_name='get_basket_data')
    direction = serializers.SerializerMethodField()
    relationtype = RelationTypeSerializer()

    # Serializes the basket depending on the destination kwarg
    def get_basket_data(self, obj):
        basket = getattr(obj, self.direction)
        basket_data = {
            'display_name': basket.display_name,
            'id': basket.id
        }

        if self.add_basket_types:
            basket_data['types'] = [t.ttype for t in basket.types.all()]

        return basket_data

    # adds direction field to serialization
    def get_direction(self, obj):
        return self.direction

    class Meta:
        model = RelatedBasket
        fields = ('id', 'relationtype', 'basket', 'direction')
