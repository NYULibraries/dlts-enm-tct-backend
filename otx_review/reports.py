import csv
import os

from django.utils import timezone
from django.conf import settings

from otcore.hit.models import Basket
from .models import Report


REPORT_QUERYSETS = {
    Report.ALL_TOPICS: Basket.objects.all(),
    Report.ALL_REVIEWED: Basket.objects.filter(review__reviewed=True),
    Report.UNCHANGED: Basket.objects.filter(review__reviewed=True, review__changed=False),
    Report.CHANGED: Basket.objects.filter(review__reviewed=True, review__changed=True),
}

REPORT_DIRECTORY = 'reports'


def generate_csv_report(report_type):
    """
    Generates a report of Reviewed models in CSV format.
    Returns a newly created Review model
    """
    sets = [topic_set[0] for topic_set in Report.TOPIC_SETS]

    assert report_type in sets, (
        "Please pass a valid report type into the generate_csv_report function. "
        "Valid options are {}. ".format(Report.TOPIC_SETS)
    )

    filename = 'report_' + timezone.localtime(timezone.now()).strftime('%Y%m%d_%H%M%S') + '.csv'
    directory = os.path.join(settings.MEDIA_ROOT, REPORT_DIRECTORY)

    os.makedirs(directory, exist_ok=True)

    full_path = os.path.join(directory, filename)

    # Fetch the associated queryset.  all() is to prevent queryset caching
    baskets = REPORT_QUERYSETS[report_type].select_related('review').order_by('-review__time').all()

    with open(full_path, 'w') as f:
        report_writer = csv.writer(f)

        report_writer.writerow([
            'Basket ID', 
            'Basket Display Name', 
            'Status',
            'Reviewed On',
            'Reviewed By'
        ])

        for basket in baskets:
            time = timezone.localtime(basket.review.time).strftime('%-m/%-d/%Y %-H:%-M:%S') if basket.review.time else None
            report_writer.writerow([
                basket.id,
                basket.display_name,
                basket.review.status,
                time,
                basket.review.reviewer,
            ])

    report = Report.objects.create(
        topic_set=report_type,
        location=os.path.join(REPORT_DIRECTORY, filename)
    )

    return report
