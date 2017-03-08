from django.contrib import admin


class HitAdmin(admin.ModelAdmin):

    fields = ('name', 'slug', 'basket', 'scope', 'preferred', 'hidden', 'kind')

    list_display = ('name', 'basket', 'preferred', 'hidden', 'kind')
    readonly_fields = ('slug',)
    search_fields = ('name', )

    def queryset(self, request):
        return super(HitAdmin, self).queryset(request).select_related('basket')


class BasketAdmin(admin.ModelAdmin):
    fields = ('label', 'display_name', 'types', )
    list_display = ('display_name', 'label',)
    search_fields = ('label', 'display_name')

    # def queryset(self, request):
    #     return super(BasketAdmin, self).queryset(request).prefetch_related('topic_hits')



class ScopeAdmin(admin.ModelAdmin):
    fields = ('id', 'scope', 'description',)
    list_display = ('id', 'scope', 'description')
