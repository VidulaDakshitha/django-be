
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.base_view import custom_exception_handler
from common.crud_mixin import CRUDMixin
from core_apps.task.models import Skill
from core_apps.task.serializers.task_serializers import SkillSerializer


# Create your views here.
class SkillView(CRUDMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = SkillSerializer
    model = Skill

    @custom_exception_handler
    def get(self, request, ):
        instances = self.model.objects.filter(is_delete=False).order_by("skill")

        keyword = request.query_params.get('keyword')

        if keyword:
            instances = instances.filter(skill__icontains=keyword)

        # page = self.paginate_queryset(instances, request)
        serializer = self.serializer_class(instances, many=True)
        return Response({"data": serializer.data})
