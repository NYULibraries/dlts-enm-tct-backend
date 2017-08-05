from rest_framework import serializers

from otcore.hit.models import Basket
from otcore.hit.serializers import HitSerializer, OccurrenceSerializer
from otcore.topic.serializers import TtypeSerializer
from otx_review.serializers import ReviewSerializer
from otx_weblink.serializers import WeblinkSerializer


class NYUBasketSerializer(serializers.ModelSerializer):
    topic_hits = HitSerializer(many=True, read_only=True)
    occurs = OccurrenceSerializer(many=True, read_only=True)
    review = ReviewSerializer()
    weblinks = WeblinkSerializer(many=True, read_only=True)
    types = TtypeSerializer(many=True, read_only=True)

    class Meta:
        model = Basket
        fields = ('id', 'topic_hits', 'occurs', 'display_name', 'description', 'review', 'weblinks', 'types')
    
