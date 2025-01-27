
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.base_view import custom_exception_handler
from common.crud_mixin import CRUDMixin
from core_apps.user.models import Locale
from core_apps.user.serializers.common_serializers import LocaleSerializer


# Create your views here.
class LanguageView(CRUDMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = LocaleSerializer
    model = Locale

    @custom_exception_handler
    def get(self, request, ):
        instances = self.model.objects.filter(is_delete=False).order_by("language")

        keyword = request.query_params.get('keyword')

        if keyword:
            instances = instances.filter(language__icontains=keyword)

        # page = self.paginate_queryset(instances, request)
        serializer = self.serializer_class(instances, many=True)
        return Response({"data": serializer.data})
