from rest_framework import serializers
from otcore.topic.models import Tokengroup, Ttype
from otcore.occurrence.models import Occurrence


class TtypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ttype
        fields = ('ttype', 'id')


class TtypeWithCountsSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()

    class Meta:
        model = Ttype
        fields = ('ttype', 'id', 'count')
