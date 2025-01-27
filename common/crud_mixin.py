from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from common.base_view import BaseView, custom_exception_handler
from utils.custom_datetime import get_formatted_current_time


class CRUDMixin(BaseView):
    serializer_class = None
    model = None

    @transaction.atomic
    @custom_exception_handler
    def post(self, request):
        with transaction.atomic():
            serializer = self.serializer_class(data=request.data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"message": "Successfully created"}, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @custom_exception_handler
    def put(self, request, object_id=None):
        with transaction.atomic():
            instance = self.get_object(self.model, object_id)
            serializer = self.serializer_class(instance, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"message": "Successfully updated"})

    @transaction.atomic
    @custom_exception_handler
    def delete(self, request, object_id=None):
        instance = self.get_object(self.model, object_id)
        instance.is_delete = True
        instance.deleted_by = request.user
        instance.deleted_on = get_formatted_current_time()
        instance.save()
        return Response({"message": "Successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
