from django.test import TestCase

from .forms import add_or_create_from_uiselect
from .models import Hit, Basket, Scope
from .processing import detach, merge_baskets
from ..relation.models import RelatedHit, RelatedBasket, RelationType
from ..occurrence.models import Occurrence, Location, Document


# Create your tests here.

class HitModelTests(TestCase):
    def test_hit_auto_slug_update(self):
        """
        Make sure that when a hit name changes, the slug auto-updates
        """
        h = Hit.objects.create(name="New York")
        self.assertEqual(h.slug, 'new-york')

        h.name = 'New York City'
        h.save()
        self.assertEqual(h.slug, 'city-new-york')

    def test_create_basket_if_needed_from_hit(self):
        """
        Create "New York"
        Check if it creates a basket with label: "new-york_0"
        """

        self.assertEqual(Basket.objects.count(), 0)

        ny = Hit(name="New York")
        ny.save()

        # NOTE: we need to look at this.  This is WAY too many queries to make a basket
        with self.assertNumQueries(13):
            ny.create_basket_if_needed()

        self.assertEqual(Basket.objects.count(), 1)

        self.assertEqual(Basket.objects.filter(label__contains="new-york_").count(), 1)

    def test_basket_display_name_auto_update(self):
        """
        Make sure that when a name changes, the basket display_name also updates
        """
        h = Hit.objects.create(name="New York")
        h.create_basket_if_needed()

        self.assertEqual(h.basket.display_name, 'New York')

        h.name = "New York City"
        h.save()

        self.assertEqual(h.basket.display_name, 'New York City')


class MergeTests(TestCase):
    def test_basic_merge(self):
        """
        Creates two separate baskets.  Merging should create only one basket
        """
        ny = Basket.create_from_string('New York')
        nyc = Basket.create_from_string('New York City')

        self.assertEqual(Basket.objects.count(), 2)

        merged = merge_baskets(ny, nyc)

        self.assertEqual(Basket.objects.count(), 1)
        self.assertEqual(merged.topic_hits.count(), 2)

    def test_merge_with_baskets_related_to_each_other(self):
        """
        If you merge two baskets related to each other, the
        relation between them should be deleted
        """
        ny = Basket.create_from_string('New York')
        nyc = Basket.create_from_string('New York City')

        RelatedBasket.objects.create(source=ny, destination=nyc)

        self.assertEqual(Basket.objects.count(), 2)
        self.assertEqual(RelatedBasket.objects.count(), 1)

        merged = merge_baskets(ny, nyc)

        self.assertEqual(Basket.objects.count(), 1)
        self.assertEqual(RelatedBasket.objects.count(), 0)

    def test_merge_with_baskets_related_to_each_other_reverse(self):
        """
        Same as above, but with the direction of the relation reversed
        """
        ny = Basket.create_from_string('New York')
        nyc = Basket.create_from_string('New York City')

        RelatedBasket.objects.create(source=nyc, destination=ny)

        self.assertEqual(Basket.objects.count(), 2)
        self.assertEqual(RelatedBasket.objects.count(), 1)

        merged = merge_baskets(ny, nyc)

        self.assertEqual(Basket.objects.count(), 1)
        self.assertEqual(RelatedBasket.objects.count(), 0)

    def test_merge_relation_shared_relation_to_different_basket(self):
        """
        If two baskets share a relation of the same type to a third basket,
        the merged basket should have only ONE copy of that relation, rather than
        a duplicate relation
        """
        ny = Basket.create_from_string('New York')
        city = Basket.create_from_string('New York City')
        state = Basket.create_from_string('New York State')

        RelatedBasket.objects.create(source=city, destination=state)
        RelatedBasket.objects.create(source=ny, destination=state)

        self.assertEqual(RelatedBasket.objects.count(), 2)

        merged = merge_baskets(ny, city)

        self.assertEqual(RelatedBasket.objects.count(), 1)
        self.assertTrue(RelatedBasket.objects.filter(source=merged, destination=state).exists(), True)

    def test_merge_relation_non_shared_relation_to_different_basket(self):
        """
        Merging baskets with relations NOT shared should just combine in the single basket
        """
        ny = Basket.create_from_string('New York')
        city = Basket.create_from_string('New York City')
        state = Basket.create_from_string('New York State')
        country = Basket.create_from_string('United States')
        borough = Basket.create_from_string('Manhattan')
        river = Basket.create_from_string('Hudson')

        # Check both directions
        RelatedBasket.objects.create(source=ny, destination=state)
        RelatedBasket.objects.create(source=country, destination=ny)

        RelatedBasket.objects.create(source=city, destination=borough)
        RelatedBasket.objects.create(source=river, destination=city)

        self.assertEqual(RelatedBasket.objects.count(), 4)

        merged = merge_baskets(ny, city)

        self.assertEqual(RelatedBasket.objects.count(), 4)

    def test_duplicate_occurence(self):
        """
        If both baskets have an occurrence to the same location, one is discarded so that there
        are no duplicate occurrences on the merged basket
        """
        document = Document.objects.create(title="Map")
        location = Location.objects.create(document=document, localid="A3", filepath="A3")

        ny = Basket.create_from_string('New York')
        nyc = Basket.create_from_string('New York City')

        Occurrence.objects.create(basket=ny, location=location)
        Occurrence.objects.create(basket=nyc, location=location)

        self.assertEqual(Occurrence.objects.count(), 2)

        merge_baskets(ny, nyc)

        self.assertEqual(Occurrence.objects.count(), 1)


class DetachTests(TestCase):
    def setUp(self):
        self.split_data = {
            'occurrences': [],
            'relations': [],
            'types': []
        }

    def test_equivalent_hits(self):
        """
        Create "New York" and "new york".
        Testing that the same slug ('new-york') is automatically merged by the 
        create_basket_if_needed() function
        """

        self.assertEqual(Basket.objects.count(), 0)

        ny = Hit(name="New York")
        ny.save()

        ny.create_basket_if_needed()

        ny = Hit(name='new york')
        ny.save()

        ny.create_basket_if_needed()

        self.assertEqual(Basket.objects.count(), 1)

        self.assertEqual(Basket.objects.filter(label__contains="new-york_").count(), 1)

    def test_delete_basket(self):
        """
        Delete a basket.  Ensure that its hits are deleted as well
        """

        self.assertEqual(Hit.objects.count(), 0)
        self.assertEqual(Basket.objects.count(), 0)

        ny = Hit(name='New York')
        ny.save()
        ny.create_basket_if_needed()

        Basket.objects.all().delete()

        self.assertEqual(Hit.objects.count(), 0)
        self.assertEqual(Basket.objects.count(), 0)

    def test_basic_detach(self):
        """
        Test that detach creates a separate basket from non-matching slug detached hit
        """
        ny = Hit(name='New York')
        ny.save()
        ny.create_basket_if_needed()

        nyc = Hit(name='New York City')
        nyc.basket = ny.basket
        nyc.save()

        self.assertEqual(Basket.objects.count(), 1)
        detach(ny, ny.basket, self.split_data)

        self.assertEqual(Hit.objects.count(), 2)
        self.assertEqual(Basket.objects.count(), 2)

    def test_slug_equivalent_detach(self):
        """
        Test detaching slug-equivalent name from basket
        Should still create a new basket rather than automatically re-merge to old basket
        """
        ny_upper = Hit(name='New York')
        ny_upper.save()
        ny_upper.create_basket_if_needed()

        ny_lower = Hit(name='new york')
        ny_lower.save()
        ny_lower.create_basket_if_needed()

        self.assertEqual(Basket.objects.count(), 1)

        detach(ny_lower, ny_upper.basket, self.split_data)

        self.assertEqual(Hit.objects.count(), 2)
        self.assertEqual(Basket.objects.count(), 2)


class BasketModelTests(TestCase):
    def test_empty_basket_display_name(self):
        """
        An empty basket's display name should include the "NO AVAILABLE NAMES" info
        """
        b = Basket.objects.create(label="Test Basket")

        self.assertEqual(b.display_name, "*NO AVAILABLE NAME* - Test Basket")

    def test_basket_display_name_is_longest_name_when_no_preferred(self):
        h = Hit.objects.create(name="New York")
        h.save()

        h.create_basket_if_needed()

        self.assertEqual(h.basket.display_name, "New York")

        h2 = Hit.objects.create(name="New York City")
        h2.basket = h.basket
        h2.save()

        self.assertEqual(h.basket.display_name, "New York City")

    def test_basket_name_updated_when_hit_deleted(self):
        """
        If a hit is deleted, make sure the basket name is appropriately recalibrated
        """
        h = Hit.objects.create(name="New York")
        h.save()

        h.create_basket_if_needed()
        basket = h.basket

        self.assertEqual(basket.display_name, "New York")

        h.delete()

        self.assertEqual(basket.display_name, "*NO AVAILABLE NAME* - {}".format(basket.label))

    def test_create_from_name_string(self):
        """
        Should create a new hit and basket from a given name string
        """
        self.assertEqual(Basket.objects.count(), 0)
        self.assertEqual(Hit.objects.count(), 0)

        basket = Basket.create_from_string('New York')

        self.assertEqual(Basket.objects.count(), 1)
        self.assertEqual(Hit.objects.count(), 1)

        self.assertEqual(basket.display_name, 'New York')

    def test_create_from_name_string_with_slug_equivalence(self):
        """
        `create_from_string` should raise an assertion error if a slug equivalent
        name already exists
        """
        Hit.objects.create(name='New York')

        with self.assertRaises(AssertionError):
            Basket.create_from_string('new york')


class HitFormTests(TestCase):
    def test_add_or_create_ui_select_new(self):
        """
        If the data from a UI Select form is -1, this means no model was selected.
        A new model should be created
        """
        self.assertEqual(Hit.objects.count(), 0)

        data = { 'id': -1, 'name': 'New York' }

        add_or_create_from_uiselect(Hit, 'name', data)

        self.assertEqual(Hit.objects.count(), 1)

        try:
            hit = Hit.objects.get(name="New York")
        except Hit.DoesNotExist:
            self.fail("Hit was not properly created by add_or_create_from_uiselect()")

    def test_add_or_create_ui_select_get(self):
        """
        if passed a different id, it should fetch that object by id
        """
        hit = Hit.objects.create(name="New York")

        data = { 'id': hit.id }

        result = add_or_create_from_uiselect(Hit, 'name', data)

        self.assertEqual(hit, result)
