import json

from otcore.hit.models import Basket

OUTFILE = "/vagrant/nyu/topics.json"

def run():
    baskets = Basket.objects.prefetch_related('topic_hits').all()
    baskets_as_dict = [
            {"id": b.id, 
             "names": [h.name for h in b.topic_hits.all()], 
             "display_name": b.display_name}
            for b in baskets]

    with open(OUTFILE, 'w') as f:
        json.dump(baskets_as_dict, f, indent=2)

