from django.test import TestCase

from .utils import clean_duplicates
from ..hit.models import Scope, Hit


class UtilityFunctionTests(TestCase):
    def test_clean_duplicates_single_field(self):
        """
        Remove duplicate models based on a single field
        """
        person = Scope.objects.create(scope="Person")
        place = Scope.objects.create(scope="Place")

        Hit.objects.create(name="Washington", scope=person)
        Hit.objects.create(name="Washington", scope=place)
        Hit.objects.create(name="Washington")
        Hit.objects.create(name="New York", scope=place)
        Hit.objects.create(name="New York")

        self.assertEqual(Hit.objects.count(), 5)

        clean_duplicates(Hit.objects.all(), ['name'])

        self.assertEqual(Hit.objects.count(), 2)
        self.assertTrue(Hit.objects.filter(name="New York").exists())
        self.assertTrue(Hit.objects.filter(name="Washington").exists())

    def test_clean_duplicates_multiple_fields(self):
        """
        Remove duplicates based on multiple fields
        """
        person = Scope.objects.create(scope="Person")
        place = Scope.objects.create(scope="Place")

        Hit.objects.create(name="Washington", scope=person, hidden=True)
        Hit.objects.create(name="Washington", scope=place, hidden=False)
        Hit.objects.create(name="Washington", hidden=True)
        Hit.objects.create(name="New York", scope=place, hidden=True)
        Hit.objects.create(name="New York", hidden=False)

        self.assertEqual(Hit.objects.count(), 5)

        clean_duplicates(Hit.objects.all(), ['name', 'hidden'])

        self.assertEqual(Hit.objects.count(), 4)
