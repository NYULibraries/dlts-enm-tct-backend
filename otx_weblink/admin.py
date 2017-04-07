from django.contrib import admin
from .models import Weblink

class WeblinkAdmin(admin.ModelAdmin):
    
    fields = [
        'url',
        'content',
        'baskets',
    ]
    list_display = ['url', 'content',]
    filter_horizontal = ('baskets',)

admin.site.register(Weblink, WeblinkAdmin)
