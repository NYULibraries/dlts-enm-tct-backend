from django.contrib import admin

# from otcore.occurrence.models import DocType
# from otcore.occurrence.models import Location
# from otcore.occurrence.models import Document
# from otcore.occurrence.models import Occurrence
# from otcore.occurrence.models import Content


class DocTypeAdmin(admin.ModelAdmin):
    fields = ('structure', )
    list_display = ('id', 'structure', )


class LocationAdmin(admin.ModelAdmin):
    fields = ('filepath', 'localid', 'document', 'content', 'context')
    list_display = ('filepath', 'prefix', 'extension', 'localid', 'document', 'context', 'content')
    search_fields = ('filepath', 'localid')
    list_filter=('document',)

class DocumentAdmin(admin.ModelAdmin):
    fields = ('title', 'author', )
    list_display = ('id', 'title', 'author',)


class OccurrenceAdmin(admin.ModelAdmin):
    fields = ('location', 'hit_in_content', 'basket', )
    list_display = ('id', 'location', 'hit_in_content')


class ContentAdmin(admin.ModelAdmin):
    fields = ('content_unique_indicator', 'content_descriptor', 'text')
    list_display = ('content_unique_indicator', 'content_descriptor', 'text')


# admin.site.register(DocType, DocTypeAdmin)
# admin.site.register(Location, LocationAdmin)
# admin.site.register(Occurrence, OccurrenceAdmin)
# admin.site.register(Document, DocumentAdmin)
# admin.site.register(Content, ContentAdmin)
