from rest_framework import serializers
from otcore.lex.models import StopWord, Acronym, Expression, Irregular


class StopWordSerializer(serializers.ModelSerializer):

    class Meta:
        model = StopWord
        fields = ('word', )


class AcronymSerializer(serializers.ModelSerializer):

    class Meta:
        model = Acronym
        fields = ('id', 'acronym', 'developed', 'active', 'rationale',)


class ExpressionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expression
        fields = ('expression', 'id',)


class IrregularSerializer(serializers.ModelSerializer):

    class Meta:
        model = Irregular
        fields = ('word', 'token')
