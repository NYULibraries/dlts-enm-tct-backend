from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from otcore.settings import otcore_settings


class StopWord(models.Model):
    """
    Stop words will be discarded and will not be transformed into tokens.
    """
    word = models.SlugField(max_length=50, unique=True, db_index=True, allow_unicode=True)

    def __str__(self):
        return self.word

    class Meta:
        ordering = ('word',)


@receiver(post_save, sender=StopWord, dispatch_uid='recache_stopwords')
def recache_stopwords(*args, **kwargs):
    if otcore_settings.CACHE_STOPWORDS:
        stopwords = StopWord.objects.values_list('word', flat=True) 
        cache.set('stopwords', stopwords)

        return stopwords


class Recognizer(models.Model):
    """
    regex-based match and replace
    """
    description = models.CharField(max_length=256, blank=True)

    recognizer = models.CharField(max_length=100)
    replacer = models.SlugField(max_length=100, allow_unicode=True)

    priority = models.FloatField(default=1.0)
    passthrough = models.BooleanField(default=False)

    class Meta:
        ordering = ('priority', )

    def __str__(self):
        return '{} | {}'.format(self.recognizer, self.replacer)


@receiver(post_save, sender=Recognizer, dispatch_uid='recache_recognizers')
def recache_recognizers(*args, **kwargs):
    if otcore_settings.CACHE_RECOGNIZERS:
        recognizers = list(Recognizer.objects.all())
        cache.set('recognizers', recognizers)

        return recognizers
