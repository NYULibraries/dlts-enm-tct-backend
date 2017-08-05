import itertools

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError
from autoslug import AutoSlugField

from otcore.lex.lex_utils import lex_slugify
from otcore.topic.models import Tokengroup
from otcore.relation.models import RelatedBasket
from otcore.management.common import substring_before
from otcore.settings import otcore_settings


def pop_from(instance):
    """
    Legacy function required for migrations
    """
    return instance.name


class Scope(models.Model):
    """
    Scope is the way to disambiguate between names using the same string. 
    For example: New York (scope:City) and New York (scope:State).
    """
    scope = models.CharField(max_length=100, null=False, unique=True, 
                             default='Generic', db_index=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.scope

    def get_absolute_url(self):
        return reverse('scope-detail', args=[self.slug])


class Basket(models.Model):
    """
    A basket is a container that groups the various hits being used as a topic name.
    The label of a basket is identical to the topic identifier.
    """
    label = models.CharField(max_length=512, db_index=True)
    types = models.ManyToManyField('topic.Ttype', blank=True, related_name="baskets")
    tokengroups = models.ManyToManyField('topic.Tokengroup', blank=True)
    display_name = models.CharField(max_length=512, blank=True)
    description = models.TextField(blank=True)

    # Remove categories because a topic can have mulltiple types, and then it's a matter of querying on intersection of types.

    """
    Number of names for the topic.
    """
    @property
    def number_of_names(self):
        return len(self.topic_hits.all())

    def local_tokengroup(self):

        """
        Creates token groups for the current basket.
        """

        slugs = '-'.join([hit.slug for hit in self.topic_hits.all()])

        alltokens = '-'.join(list(set(slugs.split('-'))))
        tokens = alltokens.split('-')

        # Only make token groups if there are more then a certain number of words in the name.
        if len(tokens) >= otcore_settings.MULTIPLE_RELATIONS_COUNT:
            tokengroups = ['-'.join(sorted(list(x))) for x in itertools.combinations(tokens, otcore_settings.MULTIPLE_RELATIONS_COUNT)]
            tokengroup_objects = []
            for tokengroup in tokengroups:
                tokengroup_objects.append(Tokengroup.objects.get_or_create(group=tokengroup)[0])

            self.tokengroups.add(*tokengroup_objects)

    @property
    def related_baskets(self):
        """
        This works best for generic, symmetrical relationships (no role_from, role_to)
        """
        related_topics = set()
        for rbasket in RelatedBasket.objects.filter(source=self):
            related_topics.add(rbasket.destination)
        for rbasket in RelatedBasket.objects.filter(destination=self):
            related_topics.add(rbasket.source)
        return list(related_topics)

    def update_display_name(self, save_on_change=True):
        current_display_name = self.display_name
        topic_hits = self.topic_hits.all()

        if len(topic_hits) == 0:
            # If there is only one name, consider it as the preferred name.
            # But don't save it as a preferred_name in Hit.
            self.display_name = '*NO AVAILABLE NAME* - {}'.format(self.label)
        elif len([hit for hit in topic_hits if hit.hidden == False]) == 0:
            # If all names are hidden, report a dummy name "*NO VISIBLE NAME*"
            self.display_name = '*NO VISIBLE NAME* - {}'.format(self.label)
        else:
            try:
                # If one of the names has preferred set to True, take it.
                preferred = [hit for hit in topic_hits if hit.preferred == True][0]
                display_name = preferred.name
            except IndexError:
                # Otherwise. No preferred name on the basket, no hit is preferred.
                # Take the longest name available
                names = [hit.name for hit in topic_hits if hit.hidden is False]
                display_name = max(names, key=len)

            self.display_name = display_name

        if save_on_change and self.display_name != current_display_name:
            self.save()

    # If there is no preferred name, populates it based on the current set of names
    # to change the preferred name, always use the hit.set_preferred() function, which will update the basket
    def save(self, *args, **kwargs):
        self.update_display_name(save_on_change=False)

        return super(Basket, self).save(*args, **kwargs)

    @property
    def longest_name(self):
        names = [hit.name for hit in self.topic_hits.all()]
        return max(names, key=len)

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['display_name', ]

    @staticmethod
    def create_from_string(name_string):
        """
        Creates a hit from a name string.  Does not handle disambiguation, so simply raises an
        exception if a slug equivalent string exists
        """
        slug = lex_slugify(name_string)

        assert not Hit.objects.filter(slug=slug).exists(), (
            "A Hit with slug {}, created from {}, already exists.  The `create_from_string` function does "
            "not handle disambiguation.  Pleace create basket by different means."
        )

        hit = Hit.objects.create(name=name_string)
        hit.create_basket_if_needed()

        return hit.basket


def get_default_scope():
    scope, _ = Scope.objects.get_or_create(scope="Generic")
    return scope.id


class Hit(models.Model):

    """
    Hit represents the information as it is found in the sources. It's the characters strings as extracted from source documents, index entries, or external knowledge base files such as hubtop.

    'name' is the character string itself.

    'bypass' indicates whether a given string, if found, should be ignored and not be part of the topic map. For example, if the topics are acquired from extracting from headers, and a header is "Table 1", bypass can be used to exclude it from appearing in the topic map. 'bypass' differs from a deletion, because bypass is a permanent marker for exclusion: each time the same string will pop up in a new context, it will be excluded.

    'slug' is an automatically created field that aims at "normalizing" the spelling, so that alternative spellings would end up producing the same topic. Rules for transforming a name into a slug can be customized using stop words, expressions (words to keep together as a unit), custom (irregular) transformations, and acronyms.

    'scope' is an attribute that is used to differentiate domains in which a topic name is valid. The same name could be used to describe different topics (homonyms). For example, "New York" can be used for the city or for the state. Adding scopes to the name is used to create distinct topics.

    'error' refers to a processing error indicating that the hit didn't make it through and explaining why.
    """

    name = models.CharField(max_length=512, db_index=True)

    # Extra property for names.
    # Note. Will be used for acronyms.
    kind = models.CharField(max_length=15, null=True, blank=True)

    slug = AutoSlugField(max_length=512, populate_from='name', slugify=lex_slugify, unique=False, always_update=True)
    scope = models.ForeignKey('Scope', default=get_default_scope, on_delete=models.CASCADE, related_name='hits')  # Default = Generic

    hidden = models.BooleanField(default=False)
    preferred = models.BooleanField(default=False)
    bypass = models.BooleanField(default=False)

    basket = models.ForeignKey(Basket, related_name='topic_hits', null=True, blank=True, on_delete=models.CASCADE)

    @property
    def tokens(self):
        return set(self.slug.split('-'))

    def __str__(self):
        name = self.name

        if self.scope_id != 0:
            name += " [as " + self.scope.scope + "]"

        return name

    def equivalents(self):
        return [hit for hit in Hit.objects.filter(slug=self.slug, scope=self.scope).exclude(name=self.name)]

    def create_basket_if_needed(self, force=False):
        # If there is another name with the same slug, use that basket.
        if not force:
            for equivalent in self.equivalents():
                if equivalent.basket is not None:
                    self.basket = equivalent.basket
                    self.save()
                    self.basket.save()
                    break

        # If the basket already exists, don't do anything
        # Otherwise, create a new basket.
        if not self.basket:
            label = '%s%s%s' % (self.slug, otcore_settings.SCOPE_SEPARATOR, self.scope.id)

            basket = Basket.objects.create(label=label)
            self.basket = basket

            self.save()

    def set_bypass(self, bypass_val):
        """
        Sets the bypass attribute for the hit.
        Expects a boolean true/false value
        If setting to true, it will take the hit off its current basket.
        If setting to false, it will attach the hit to the relevant basket (and create one if needed)
        """

        if (bypass_val and self.bypass) or (not bypass_val and not self.bypass):
            # Submitted value matches current attribute.  Do nothing
            pass

        else:
            if bypass_val:
                self.bypass = True
                basket = self.basket
                self.basket = None
                self.save()

                if basket and basket.topic_hits.count() == 0:
                    basket.delete()

            else:
                self.bypass = False
                self.save()
                self.create_basket_if_needed()

    # Use to set a hit as preferred
    # Will ensure that no other hits on a topic are marked as preferred as well
    def make_preferred(self, force=False, save=True):
        # ignore for bypassed and basket-less hits
        # or if the current hit is already preferred
        if self.bypass or not self.basket or self.preferred and not force:
            pass
        else:
            # Mark any other preferred names as not preferred
            for hit in Hit.objects.filter(basket=self.basket, preferred=True).exclude(id=self.id):
                hit.preferred = False
                hit.save()

            self.preferred = True
            self.hidden = False

            self.basket.display_name = self.name
            self.basket.save()
            
            if save:
                self.save()

    # only use this to set hit as hidden
    def set_hidden(self, hidden_val):
        # ignore if bypassed and/or basketless or hidden value isn't changing
        # or this is the only name on the topic
        if self.bypass or not self.basket or self.hidden == hidden_val:
            pass
        else:
            other_names = self.basket.topic_hits.exclude(id=self.id)
            visible_names = [x for x in other_names if not x.hidden]

            # if trying to set hidden to True and there are no other visible names, raise Exception
            if hidden_val and len(visible_names) == 0:
                raise FieldError('You cannot set all names on a topic to hidden')

            self.hidden = hidden_val
            self.save()

    def save(self, *args, **kwargs):
        super(Hit, self).save(*args, **kwargs)

        if self.basket:
            self.basket.update_display_name()

        
    class Meta:
        ordering = ['name', ]
        unique_together = (('name', 'scope'))


def update_display_name_on_hit_delete(sender, instance, **kwargs):
    """
    Function to make sure basket display names are properly recalculated when a hit is 
    deleted
    """
    try:
        if instance.basket:
            instance.basket.update_display_name()
    except Basket.DoesNotExist:
        pass


models.signals.post_delete.connect(
    update_display_name_on_hit_delete, 
    sender=Hit, 
    weak=False, 
    dispatch_uid='models.update_display_name_on_hit_delete'
)
