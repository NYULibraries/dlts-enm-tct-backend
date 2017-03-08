from django.test import TestCase

from otcore.hit.models import Basket
from otcore.relation.models import RelatedBasket, RelationType
from .processing import nyu_process_single_basket, get_main_entry, get_shared_main_entry, get_rtypes, \
        nyu_global_multiple_tokens, delete_multiple_tokens_from_shared_subentries


class SubentryFunctionTests(TestCase):
    def setUp(self):
        self.rtypes = get_rtypes()

    def test_get_main_entry(self):
        """
        Check that the `get_main_entry` returns the main entry of a subentry
        """
        main_entry = Basket.create_from_string('New York')
        subentry = Basket.create_from_string('New York -- Brooklyn')

        RelatedBasket.objects.create(
            source=main_entry, destination=subentry,
            relationtype=self.rtypes['subentry']
        )

        target = get_main_entry(subentry, rtypes=self.rtypes)

        self.assertEqual(target[0], main_entry)

    def test_get_main_without_giving_rtypes(self):
        """
        `get_main_entry` should work identically without manually passing rtypes
        """
        main_entry = Basket.create_from_string('New York')
        subentry = Basket.create_from_string('New York -- Brooklyn')

        RelatedBasket.objects.create(
            source=main_entry, destination=subentry,
            relationtype=self.rtypes['subentry']
        )

        target = get_main_entry(subentry)

        self.assertEqual(target[0], main_entry)

    def test_get_main_entry_when_not_subentry(self):
        """
        Calling `get_main_entry` on a basket that isn't a subentry should return none
        """
        basket = Basket.create_from_string('New York')

        target = get_main_entry(basket, rtypes=self.rtypes)

        self.assertIsNone(target)

    def test_shared_main_entry(self):
        """
        calling `get_shared_main_entry` should return a common main entry
        basket when two subentries are passed
        """
        main_entry = Basket.create_from_string('New York')
        first_subentry = Basket.create_from_string('New York -- Brooklyn')

        RelatedBasket.objects.create(
            source=main_entry, destination=first_subentry,
            relationtype=self.rtypes['subentry']
        )

        second_subentry = Basket.create_from_string('New York -- Manhattan')

        RelatedBasket.objects.create(
            source=main_entry, destination=second_subentry,
            relationtype=self.rtypes['subentry']
        )

        target = get_shared_main_entry(first_subentry, second_subentry, rtypes=self.rtypes)

        self.assertEqual(target, main_entry)

    def test_shared_main_entry_without_valid_baskets(self):
        """
        calling `get_shared_main_entry` when two entries AREN'T subentries of a common
        topic should return None
        """
        basket1 = Basket.create_from_string('New York')
        basket2 = Basket.create_from_string('Mineola')

        target = get_shared_main_entry(basket1, basket2, rtypes=self.rtypes)

        self.assertIsNone(target)


class NYUMultipleTokenTests(TestCase):
    def assertMultipleTokens(self, basket1, basket2):
        self.assertTrue(
            RelatedBasket.objects.filter(
                source=basket1, destination=basket2, relationtype=self.rtypes['multipletokens']
            ) or RelatedBasket.objects.filter(
                destination=basket1, source=basket2, relationtype=self.rtypes['multipletokens']
            ))

    def assertNotMultipleTokens(self, basket1, basket2):
        self.assertFalse(
            RelatedBasket.objects.filter(
                source=basket1, destination=basket2, relationtype=self.rtypes['multipletokens']
            ) or RelatedBasket.objects.filter(
                destination=basket1, source=basket2, relationtype=self.rtypes['multipletokens']
            ))

    def setUp(self):
        self.rtypes = get_rtypes()

    def test_regular_multiple_tokens(self):
        """
        When entries aren't subentries of a common main topic, regular
        subentry rules should apply
        """
        basket1 = Basket.create_from_string('New York City Police Department')
        basket2 = Basket.create_from_string('New York Department of Works')
        basket3 = Basket.create_from_string('New York City')

        self.assertEqual(RelatedBasket.objects.filter(relationtype=self.rtypes['multipletokens']).count(), 0)

        nyu_global_multiple_tokens()

        self.assertMultipleTokens(basket1, basket2)
        self.assertMultipleTokens(basket1, basket3)
        self.assertNotMultipleTokens(basket2, basket3)

    def test_subentry_multiple_tokens(self):
        """
        Tests that the following rules apply
            1. if a pair of topics are sub/main entry pair, no relation is created between them
            2. if two topics share a main entry but don't have any more tokens in common than those in the main
                entry, no relation is created between them
            3. if the two topics share a main entry and have additional tokens in common, they are related
        """
        main_entry = Basket.create_from_string('New York City')
        first_subentry = Basket.create_from_string('New York City -- Brooklyn')

        RelatedBasket.objects.create(
            source=main_entry, destination=first_subentry,
            relationtype=self.rtypes['subentry']
        )

        second_subentry = Basket.create_from_string('New York City -- Manhattan')

        RelatedBasket.objects.create(
            source=main_entry, destination=second_subentry,
            relationtype=self.rtypes['subentry']
        )

        third_subentry = Basket.create_from_string('New York City -- Brooklyn Brewery')

        RelatedBasket.objects.create(
            source=main_entry, destination=third_subentry,
            relationtype=self.rtypes['subentry']
        )

        nyu_global_multiple_tokens()

        self.assertNotMultipleTokens(main_entry, first_subentry) # no relation between sub/main entries
        self.assertNotMultipleTokens(first_subentry, second_subentry) # no relation between subentries without extra tokens
        self.assertMultipleTokens(first_subentry, third_subentry) # relation between subentries WITH extra tokens

    def test_nyu_multiple_tokens_from_single_basket(self):
        """
        Same as above test, but using the `nyu_process_single_basket` function
        """
        main_entry = Basket.create_from_string('New York City')
        first_subentry = Basket.create_from_string('New York City -- Brooklyn')

        RelatedBasket.objects.create(
            source=main_entry, destination=first_subentry,
            relationtype=self.rtypes['subentry']
        )

        second_subentry = Basket.create_from_string('New York City -- Manhattan')

        RelatedBasket.objects.create(
            source=main_entry, destination=second_subentry,
            relationtype=self.rtypes['subentry']
        )

        third_subentry = Basket.create_from_string('New York City -- Brooklyn Brewery')

        RelatedBasket.objects.create(
            source=main_entry, destination=third_subentry,
            relationtype=self.rtypes['subentry']
        )

        nyu_process_single_basket(first_subentry, run_containment=False)

        self.assertNotMultipleTokens(main_entry, first_subentry) # no relation between sub/main entries
        self.assertNotMultipleTokens(first_subentry, second_subentry) # no relation between subentries without extra tokens
        self.assertMultipleTokens(first_subentry, third_subentry) # relation between subentries WITH extra tokens

    def test_delete_shared_subentries(self):
        """
        `delete_multiple_tokens_from_shared_subentries` should remove MultipleToken relations from topic
        pairs with the same main entry.  All others should be left intact
        """
        main_entry = Basket.create_from_string('New York City')
        first_subentry = Basket.create_from_string('New York City -- Brooklyn')

        RelatedBasket.objects.create(
            source=main_entry, destination=first_subentry,
            relationtype=self.rtypes['subentry']
        )

        second_subentry = Basket.create_from_string('New York City -- Brooklyn Bowl')

        RelatedBasket.objects.create(
            source=main_entry, destination=second_subentry,
            relationtype=self.rtypes['subentry']
        )

        other = Basket.create_from_string('Museum of the City of New York')

        nyu_global_multiple_tokens()

        self.assertEqual(RelatedBasket.objects.filter(relationtype=self.rtypes['multipletokens']).count(), 4)
        self.assertMultipleTokens(first_subentry, second_subentry)

        delete_multiple_tokens_from_shared_subentries()

        self.assertEqual(RelatedBasket.objects.filter(relationtype=self.rtypes['multipletokens']).count(), 3)
        self.assertNotMultipleTokens(first_subentry, second_subentry)
