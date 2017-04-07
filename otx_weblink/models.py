from django.db import models


class Weblink(models.Model):
    url = models.URLField(max_length=500, blank=True, null=True)
    content = models.CharField(max_length=500, blank=True, null=True)
    baskets = models.ManyToManyField('hit.Basket', blank=True, related_name='weblinks')

    def __str__(self):
        return '<a href="%s">%s</a>' % (self.url, self.content)
