from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import serializers

from otcore.hit.models import Hit, Basket
from .models import Review, Report


class UserField(serializers.RelatedField):
    queryset = User.objects.all()

    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        return self.queryset.get(id=data)


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserField() 

    class Meta:
        model = Review
        fields = ('reviewer', 'time', 'reviewed', 'changed')


class HitListWithReviewSerializer(serializers.ModelSerializer):
    scope = serializers.StringRelatedField()
    review = ReviewSerializer(source='basket.review')

    class Meta:
        model = Hit
        fields = ('name', 'basket', 'scope', 'preferred', 'hidden', 'id', 'review')


class BasketListWithReviewSerializer(serializers.ModelSerializer):
    review = ReviewSerializer()

    class Meta:
        model = Basket
        fields = ('id', 'display_name', 'review')


class BasketListWithReviewAndCountsSerializer(serializers.ModelSerializer):
    review = ReviewSerializer()
    occurrence_counts = serializers.IntegerField()

    class Meta:
        model = Basket
        fields = ('id', 'display_name', 'review', 'occurrence_counts')
        

# With thanks to: 
# http://stackoverflow.com/questions/17331578/django-rest-framework-timezone-aware-renderers-parsers
class LocalDateTimeField(serializers.DateTimeField):

    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(LocalDateTimeField, self).to_representation(value)


class ReportSerializer(serializers.ModelSerializer):
    time = LocalDateTimeField(format='%B %-d, %Y, %H:%M:%S')
    topic_set = serializers.SerializerMethodField()

    def get_topic_set(self, obj):
        return obj.get_topic_set_display()

    class Meta:
        model = Report
        fields = ('id', 'topic_set', 'location', 'time')
