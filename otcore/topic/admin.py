from django.contrib import admin

# from otcore.topic.models import Tokengroup, Ttype


class TokengroupAdmin(admin.ModelAdmin):
    fields = ('group',)
    list_display = ('group',)


class TtypeAdmin(admin.ModelAdmin):
    fields = ('ttype',)
    list_display = ('ttype',)

# admin.site.register(Tokengroup, TokengroupAdmin)
# admin.site.register(Ttype, TtypeAdmin)
