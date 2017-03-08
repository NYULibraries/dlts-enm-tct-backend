from django.contrib import admin
# from otcore.lex.models import StopWord, Acronym, Expression, Irregular


class StopWordAdmin(admin.ModelAdmin):
    fields = ('word',)

# admin.site.register(StopWord, StopWordAdmin)


class AcronymAdmin(admin.ModelAdmin):
    fields = ('acronym', 'developed', 'active', 'rationale',)
    list_display = ('acronym', 'developed', 'active', 'rationale',)

# admin.site.register(Acronym, AcronymAdmin)


class ExpressionAdmin(admin.ModelAdmin):
    fields = ('expression',)
    list_display = ('expression',)

# admin.site.register(Expression, ExpressionAdmin)


class IrregularAdmin(admin.ModelAdmin):
    fields = ('word', 'token',)
    list_display = ('word', 'token')

# admin.site.register(Irregular, IrregularAdmin)
