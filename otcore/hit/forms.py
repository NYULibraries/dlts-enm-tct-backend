
from django import forms

from otcore.hit.models import Hit


def add_or_create_from_uiselect(model, field_name, data):

    if data['id'] == -1:
        obj = model()
        setattr(obj, field_name, data[field_name])
        obj.save()
    else:
        obj = model.objects.get(id=data['id'])

    return obj
