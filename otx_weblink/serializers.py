from rest_framework import serializers
from .models import Weblink


class WeblinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Weblink
        fields = ('id',  'content', 'url')
