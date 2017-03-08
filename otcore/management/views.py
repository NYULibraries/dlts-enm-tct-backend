from django.views.generic import TemplateView
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
# from django.contrib.auth.mixins import LoginRequiredMixin

from otcore.management.manage_utils import get_statistics


# Reusable API views
class DeleteIfUnusedMixin():
    # A list of fields to check as to whether or not they will be empty when you remove this object
    check_fields = None
    # The specific field you're removing this object from
    detach_field = None

    # Validation check function
    def get_check_fields(self):
        assert self.check_fields is not None, (
            "'%s' should either include a `check_fields` attribute, "
            "or override the `get_check_fields()` method."
            % self.__class__.__name__
        )

        assert isinstance(self.check_fields, list) or isinstance(self.check_fields, tuple), (
            "`check_fields` attribute should be either a list or a tuple."
        )

        return self.check_fields

    # Validation check function
    def get_detach_field(self):
        assert self.detach_field is not None, (
            "'%s' should either include a `detach_field` attribute, "
            "or override the `get_detach_field()` method."
            % self.__class__.__name__
        )

        assert self.detach_field in self.check_fields, (
            "`detach_field` attribute needs to be in the `check_fields` list"
        )

        return self.detach_field

    # Goes through listed related fields and checks if there are other relations
    # If there are, it removes the relation from the current model
    # If not, it deletes the instance entirely
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()

        check_fields = self.get_check_fields()
        detach_field = self.get_detach_field()

        for field in check_fields:
            if field == detach_field:
                detach_from = getattr(instance, field).get(id=request.data['detach_id'])
                getattr(instance, field).remove(detach_from)

            if getattr(instance, field).count() > 0:
                return Response(status=status.HTTP_204_NO_CONTENT)

        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
