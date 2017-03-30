import json

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .processing import reconcile


class ProcessReconciliationView(APIView):
    def post(self, request, *args, **kwargs):
        json_file = request.data['file'].read()

        try:
            reconciliation_data = json.loads(json_file.decode('utf-8'))
        except (json.decoder.JSONDecodeError, UnicodeDecodeError):
            return Response({"non_field_errors": ["Not a valid JSON file."]}, status=status.HTTP_400_BAD_REQUEST)

        errors = reconcile(reconciliation_data)

        return Response(errors)
