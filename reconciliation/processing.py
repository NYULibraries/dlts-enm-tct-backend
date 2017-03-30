from django.db.utils import IntegrityError

from otcore.hit.models import Basket, Hit
from otcore.topic.models import Ttype
from otx_weblink.models import Weblink


def reconcile(reconciliation_data):
    """
    Pass a python dict of reconciliation data of the form:
    {
        "basket": BASKET_ID,
        "external_link": {
            "URL": "URI_TO_EXTERNAL_SOURCE",
            "label": "SOURCE_NAME",
            "link_type": "exactMatch/fuzzyMatch",
            "recon_data": {
                "topic_hits": [TOPIC_NAMES_LIST],
                "topic_type": "TOPIC_TYPE"
            }
        }
    },
    """
    errors = []

    for basket_data in reconciliation_data:
        try:
            basket = Basket.objects.get(id=basket_data['basket'])
        except Basket.DoesNotExist:
            errors.append("Topic {0}: No topic matches basket id {0}".format(basket_data['basket']))
            continue

        url = basket_data['external_link'].get('URL', None)
        label = basket_data['external_link'].get('label', None)
        link_type = basket_data['external_link'].get('link_type', None)

        if url is not None and label is not None and link_type is not None:
            weblink, _ = Weblink.objects.get_or_create(
                url=url, content='{} ({})'.format(label, link_type)
            )
            weblink.baskets.add(basket)

        recon_data = basket_data['external_link'].get('recon_data', None)

        if recon_data is not None:
            topic_hits = recon_data.get('topic_hits', [])

            for name in topic_hits:
                try: 
                    Hit.objects.get_or_create(
                        name=name, basket=basket
                    )
                except IntegrityError:
                    errors.append("Topic {}: Name \"{}\" already exists on a different topic.".format(basket.id, name))

            topic_types = recon_data.get('topic_type', [])

            for topic_type in topic_types:
                ttype, _ = Ttype.objects.get_or_create(ttype=topic_type)
                basket.types.add(ttype)

    return errors
