import os
import bisect
from functools import reduce

from otcore.hit.models import Basket


def read_files(top_directory):

    """
    Returns a list of all files within a hierarchical directory
    structure starting from top.
    """

    filelist = []
    for path, dirs, files in os.walk(top_directory, topdown=True):
        for filename in files:
            if not filename.endswith('~') and filename != '.DS_Store':
                filelist.append(os.path.join(path, filename))
    return filelist


def create_occurrence_rings(location_data):
    """
    Given an array of location data, adds occurrence ring info
    """
    data_with_ring = []

    if isinstance(location_data, dict):
        location_data = [location_data]

    basket_ids = reduce(lambda x, y: x + [b['basket']['id'] for b in y['occurrences']], location_data, [])
    baskets = Basket.objects.filter(id__in=basket_ids).prefetch_related('occurs')

    by_basket = {x.id: [{'id': y.id,  'location': y.location_id} for y in x.occurs.all()] for x in baskets}

    for location in location_data:
        for occ in location['occurrences']:
            others = [x['location'] for x in by_basket[occ['basket']['id']] if occ['id'] != x['id']]
            others.sort()

            if len(others) == 0:
                occ['ring_next'] = None
                occ['ring_prev'] = None

            elif len(others) == 1:
                occ['ring_next'] = others[0]
                occ['ring_prev'] = others[0]

            else:
                bisect_index = bisect.bisect(others, location['id'])
                occ['ring_next'] = others[0] if bisect_index >= len(others) else others[bisect_index]
                occ['ring_prev'] = others[len(others)-1] if bisect_index == 0 else others[bisect_index - 1]

    return location_data
            
