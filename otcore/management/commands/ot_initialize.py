from django.core.management.base import BaseCommand

from otcore.management.manage_utils import initialize


class Command(BaseCommand):

    can_import_settings = True

    help = 'Set Initial Values'

    def handle(self, *args, **options):
        initialize()
