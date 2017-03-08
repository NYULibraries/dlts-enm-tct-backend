from django.test import TestCase

from otcore.hit.models import Basket
from otcore.relation.models import RelatedBasket

from .processing import global_containment, process_single_basket


class ContainmentTests(TestCase):
    def assertIsContained(self, source_basket, destination_basket):
        self.assertTrue(RelatedBasket.objects.filter(source=source_basket, destination=destination_basket).exists())

    def assertIsNotContained(self, source_basket, destination_basket):
        self.assertFalse(RelatedBasket.objects.filter(source=source_basket, destination=destination_basket).exists())

    def test_basic_containment(self):
        """
        Tests a simple case of containment, with a smaller hit
        """
        basket1 = Basket.create_from_string("Crosby, Stills, and Nash")

        basket2 = Basket.create_from_string("Crosby, Stills, Nash, and Young")

        process_single_basket(basket1)

        self.assertIsContained(basket1, basket2)


    def test_reverse_containment(self):
        """
        Tests reverse containment, using a larger basket
        """
        basket1 = Basket.create_from_string("Crosby, Stills, and Nash")

        basket2 = Basket.create_from_string("Crosby, Stills, Nash, and Young")

        process_single_basket(basket2)

        self.assertIsContained(basket1, basket2)


    def test_failing_containment(self):
        """
        Checks that two hits without contained slugs don't create
        a containment relation
        """
        basket1 = Basket.create_from_string("Crosby, Stills, and Nash")

        basket2 = Basket.create_from_string("Medeski, Martin, and Wood")

        process_single_basket(basket1)

        self.assertIsNotContained(basket1, basket2)

    def test_non_consecutive_slugs(self):
        """
        Checks for bug where nonconsecutive slugs (eg:
            'israel-zangwill'
            'israel-melte-pot-zangwill'
        ) still create proper containment
        """
        basket1 = Basket.create_from_string("Zangwill, Israel")

        basket2 = Basket.create_from_string("Zangwill, Israel, The Melting Pot")

        process_single_basket(basket1)

        self.assertIsContained(basket1, basket2)

    def test_global_slug_processing(self):
        """
        Tests that global containment catches all relevant containments (and 
        doesn't create any extra relations
        """
        basket1 = Basket.create_from_string("Zangwill, Israel")
        basket2 = Basket.create_from_string("Zangwill, Israel, The Melting Pot")
        basket3 = Basket.create_from_string("Crosby, Stills, and Nash")
        basket4 = Basket.create_from_string("Crosby, Stills, Nash, and Young")
        basket5 = Basket.create_from_string("John Nash")
        basket6 = Basket.create_from_string("Nash")

        global_containment()

        self.assertEqual(RelatedBasket.objects.count(), 5)
