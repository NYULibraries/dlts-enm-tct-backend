from django.contrib import admin
# from otcore.relation.models import RelatedBasket, RelatedHit, RelationType


class RelatedBasketAdmin(admin.ModelAdmin):
    fields = ['source', 'destination', 'relationtype', 'origins']
    list_display = ['source', 'destination', 'relationtype', ]

# admin.site.register(RelatedBasket, RelatedBasketAdmin)
