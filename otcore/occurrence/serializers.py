from rest_framework import serializers

from .models import Location, Document, Occurrence, Content
from .processing import create_occurrence_rings
from otcore.hit.models import Basket


class ContentSerializer(serializers.ModelSerializer):
    class Meta:

        model = Content
        fields = (
            'content_unique_indicator',
            'content_descriptor',
            'text',
        )


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ('title', 'author')


class DocumentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ('title', 'author', 'id')


class LocationSerializer(serializers.ModelSerializer):
    document = DocumentSerializer()

    class Meta:
        model = Location
        fields = ( 'id', 'document', 'localid', 'sequence_number')


class ContentTextOnlyField(serializers.RelatedField):
    """
    Get the first 100 characters
    """
    def to_representation(self, value):
        text = value.text[:100]

        if len(value.text) > 100:
            text += '...'

        return text


class LocationListSerializer(serializers.ModelSerializer):
    content = ContentTextOnlyField(read_only=True)

    class Meta:
        model = Location
        fields = ('id', 'localid', 'sequence_number', 'content')


class DocumentDetailSerializer(serializers.ModelSerializer):
    locations = LocationListSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = ('author', 'title', 'locations')


class OccurrenceSerializer(serializers.ModelSerializer):
    """
    Serializer for occurrence gives full location and document information, but no basket information.
    Mostly for use on basket detail pages
    """
    location = LocationSerializer()

    class Meta:
        model = Occurrence
        fields = ( 'id', 'location', 'basket',)


class BasketSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = ('id', 'display_name')


class OccurrenceFromLocationSerializer(serializers.ModelSerializer):
    basket = BasketSimpleSerializer(read_only=True)

    class Meta:
        model = Occurrence
        fields = ('basket', 'id')


class LocationFullSerializer(serializers.ModelSerializer):

    content = ContentSerializer()
    document = DocumentSerializer()
    occurrences = OccurrenceFromLocationSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = (
            'id',
            'content',
            'document',
            'context',
            'occurrences',
            'filepath',
            'localid'
        )

    @property
    def data(self):
        """
        reprocesses the data, once the serializer has run, to add the next/previous
        occurrence instances for the creation of occurrence rings
        """
        _data = super(LocationFullSerializer, self).data

        return create_occurrence_rings(_data)

    def __init__(self, *args, **kwargs):
        """
        Allows the addition of `next_location_id` and `previous_location_id`. 
        Because those are model properties (and therefore do not benefit from prefetch_related and 
        select_related), this is off be default and must be turned on by explictly passing
        location_controls = True
        """
        location_controls = kwargs.pop('location_controls', False)

        self.Meta.fields = list(self.Meta.fields)

        if location_controls:
            self.Meta.fields += ['next_location_id', 'previous_location_id']

        super(LocationFullSerializer, self).__init__(*args, **kwargs)


class OccurrenceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occurrence
        fields = ('basket', 'location')
