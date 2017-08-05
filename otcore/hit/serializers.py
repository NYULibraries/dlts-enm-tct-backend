from rest_framework import serializers
from otcore.hit.models import Hit, Basket, Scope
from otcore.occurrence.serializers import OccurrenceSerializer
from otcore.topic.serializers import TtypeSerializer


class ScopeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Scope
        fields = ('id', 'scope', )


class ScopeWithCountsSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()

    class Meta:
        model = Scope
        fields = ('id', 'scope', 'count')


class HitNameField(serializers.Field):
    def to_representation(self, obj):
        return str(obj)

    def get_attribute(self, obj):
        return obj


class HitSerializer(serializers.ModelSerializer):
    scope = ScopeSerializer()

    class Meta:
        model = Hit
        fields = ('id', 'name', 'scope', 'bypass', 'hidden', 'preferred')


class HitCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hit
        fields = ('id', 'name', 'scope', 'bypass', 'hidden', 'preferred', 'basket')


class HitUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hit
        fields = ('id', 'name', 'hidden', 'preferred')


class HitListSerializer(serializers.ModelSerializer):
    scope = serializers.StringRelatedField()

    class Meta:
        model = Hit
        fields = ('name', 'basket', 'scope', 'preferred', 'hidden', 'id')


class BasketSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = ('id', 'display_name')


class BasketListSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        occurrence_counts = kwargs.pop('occurrence_counts', False)
        relation_counts = kwargs.pop('relation_counts', False)

        super(BasketListSerializer, self).__init__(*args, **kwargs)

        if occurrence_counts:
            self.fields['occurrence_counts'] = serializers.IntegerField()

        if relation_counts:
            self.fields['relation_counts'] = serializers.IntegerField()

    class Meta:
        model = Basket
        fields = ('id', 'display_name', )


class HitListWithBasketNamesSerializer(serializers.ModelSerializer):
    basket = BasketSimpleSerializer(read_only=True)
    scope = ScopeSerializer()

    class Meta:
        model = Hit
        fields = ('name', 'basket', 'id', 'scope')


class BasketSerializer(serializers.ModelSerializer):
    topic_hits = HitSerializer(many=True, read_only=True)
    occurs = OccurrenceSerializer(many=True, read_only=True)

    class Meta:
        model = Basket
        fields = ('id', 'topic_hits', 'occurs', 'display_name', 'description')


class BasketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = ('id', 'display_name', 'description')
