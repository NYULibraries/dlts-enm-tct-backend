import os
from collections import defaultdict

from rest_framework import serializers

from otx_epub.models import Epub
from otcore.occurrence.processing import create_occurrence_rings
from otcore.occurrence.models import Location, Document, Occurrence
from otcore.occurrence.serializers import ContentSerializer, BasketSimpleSerializer, \
    LocationListSerializer, OccurrenceFromLocationSerializer, LocationFullSerializer
from .models import Index, IndexPattern
from initial.pattern_mapping import pattern_mapping


class EpubDocumentSerializer(serializers.ModelSerializer):
    isbn = serializers.SerializerMethodField()
    
    def get_isbn(self, obj):
        return os.path.basename(obj.contents)

    class Meta:
        model = Epub
        fields = ('title', 'author', 'publisher', 'id', 'isbn')


class EpubListSerializer(serializers.ModelSerializer):
    locations = LocationListSerializer(many=True, read_only=True)
    isbn = serializers.SerializerMethodField()
    
    def get_isbn(self, obj):
        return os.path.basename(obj.contents)

    class Meta:
        model = Epub
        fields = ('title', 'author', 'publisher', 'isbn', 'locations')


class PageNumberSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        self.pattern = self.get_indexpattern(instance)
        return super(PageNumberSerializer, self).to_representation(instance)

    filepath = serializers.SerializerMethodField()
    xpath = serializers.SerializerMethodField()
    css_selector = serializers.SerializerMethodField()
    pagenumber_tag = serializers.SerializerMethodField()

    def get_filepath(self, obj):
        return obj.filepath.split(obj.document.epub.contents)[1]

    def get_xpath(self, obj):
        return self.pattern.pagenumber_xpath_from_location(obj)

    def get_css_selector(self, obj):
        return self.pattern.pagenumber_selector_from_location(obj)

    def get_pagenumber_tag(self, obj):
        return self.pattern.pagenumber_tag_from_location(obj)

    def get_indexpattern(self, instance):
        """
        If an indexpattern is passed into context, return that. This is to prevent redundant lookups
        when `many=True`. Otherwise, fetch the indexpattern from the database using the pattern_mapping dict.
        """
        if self.context.get('indexpattern', None) is not None:
            return self.context['indexpattern']
        else:
            pattern_name = pattern_mapping[os.path.basename(instance.document.epub.contents)]
            return IndexPattern.objects.get(name=pattern_name)

    class Meta:
        model = Location
        fields = ('filepath', 'pagenumber_tag', 'css_selector', 'xpath', )


class EpubLocationFullSerializer(LocationFullSerializer):
    document = EpubDocumentSerializer(source="document.epub")
    pagenumber = PageNumberSerializer(source="*", read_only=True)

    class Meta:
        model = Location
        fields = (
            'id',
            'content',
            'document',
            'context',
            'occurrences',
            'localid',
            'pagenumber'
        )


class IndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = Index
        fields = ('url', )


class IndexPatternSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()

    def get_documents(self, obj):
        patterns_by_name = defaultdict(list)

        for key, value in pattern_mapping.items():
            patterns_by_name[value].append(key)

        pattern_docs = patterns_by_name[obj.name]
        all_docs = Document.objects.select_related('epub').all()

        return [
            { 'title': document.title, 'id': document.id } 
            for document in all_docs 
            if os.path.basename(document.epub.contents) in pattern_docs
        ]

    class Meta:
        model = IndexPattern
        fields = (
            'name',
            'description',
            'pagenumber_pre_strings',
            'pagenumber_css_selector_pattern',
            'pagenumber_xpath_pattern',
            'xpath_entry',
            'see_split_strings',
            'see_also_split_strings',
            'xpath_see',
            'xpath_seealso',
            'separator_between_sees',
            'separator_between_seealsos',
            'separator_see_subentry',
            'inline_see_start',
            'inline_see_also_start',
            'inline_see_end',
            'inline_see_also_end',
            'subentry_classes',
            'separator_between_subentries',
            'separator_between_entry_and_occurrences',
            'separator_before_first_subentry',
            'xpath_occurrence_link',
            'indicators_of_occurrence_range',
            'documents'
        )
