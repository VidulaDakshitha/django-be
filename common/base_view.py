from functools import wraps

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator


def custom_exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as ex:
            errors = []
            if isinstance(ex.detail, dict):
                for key, value in ex.detail.items():
                    errors.extend(value if isinstance(value, list) else [value])
            elif isinstance(ex.detail, list):
                errors = ex.detail
            else:
                errors.append(str(ex))

            return Response(
                {"message": "Validation error", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as ex:
            return Response({"message": "Internal server error: ", "errors": [str(ex)]},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapper


class BaseView(APIView):
    @staticmethod
    def get_object(model, object_id):
        return get_object_or_404(model, id=object_id, is_delete=False)

    @staticmethod
    def paginate_queryset(queryset, request):
        paginator = Paginator(queryset, request.query_params.get('limit', 10))
        page = paginator.get_page(request.query_params.get('page', 1))
        return page
