from rest_framework.permissions import IsAuthenticated

from common.base_permission import IsConsultantManager, CustomMethodNotAllowed, IsBilling, IsGigWorker, IsOverEmployee
from common.base_view import custom_exception_handler
from common.crud_mixin import CRUDMixin
from core_apps.task.models import SubTask

from rest_framework.response import Response

from core_apps.task.serializers.sub_task_serializer import SubTaskSerializer


class SubTaskView(CRUDMixin):
    serializer_class = SubTaskSerializer
    model = SubTask

    def get_permissions(self):
        if self.request.method in ["POST"]:
            self.permission_classes = [IsAuthenticated]
        if self.request.method in ["PUT", "DELETE"]:
            self.permission_classes = [IsAuthenticated, (IsBilling | IsOverEmployee | IsGigWorker)]
        else:
            self.permission_classes = [IsAuthenticated, ]
        return super().get_permissions()

    @custom_exception_handler
    def get(self, request, object_id=None):
        submissions = self.model.objects.filter(is_delete=False, task_id=object_id).order_by(
            "-id")

        page = self.paginate_queryset(submissions, request)
        serializer = self.serializer_class(page, many=True)
        count = submissions.count()
        return Response({"data": serializer.data, "count": count})
