from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.base_permission import IsConsultantManager, IsSales, IsGigWorker, IsCustomer, IsOverEmployee, IsTaskManager
from common.base_view import custom_exception_handler, BaseView
from common.crud_mixin import CRUDMixin
from core_apps.bid.models import Bid
from core_apps.bid.serializers.bid_serializers import BidSerializer, BidManagementSerializer, BidSummarySerializer
from core_apps.bid.serializers.task_bid_summary_serializers import TaskBidSummarySerializer
from core_apps.task.models import Task
from core_apps.user.models import User


# Create your views here.
class BidView(CRUDMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = BidSerializer
    model = Bid

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "DELETE"]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @custom_exception_handler
    def get(self, request, object_id=None):
        if object_id:
            task = self.get_object(self.model, object_id)
            serializer = self.serializer_class(task)
            return Response(serializer.data)
        else:
            origin = request.query_params.get('origin', None)
            worker = request.query_params.get('worker', None)
            bid_type = request.query_params.get('bid_type', None)
            keyword = request.query_params.get('keyword', None)

            if origin is not None and origin:
                task_id = request.query_params.get('task_id', None)
                if request.user.has_organization:
                    if request.user.has_any_role([User.ADMIN_ROLE, User.TASK_MANAGER_ROLE]):
                        bids = Bid.objects.filter(task_id=task_id).order_by("-id")
                    else:
                        raise Exception("User is not authorized to view this page")
                else:
                    bids = Bid.objects.filter(task_id=task_id).order_by("-id")
            elif worker is not None and worker:
                if request.user.has_organization:
                    if request.user.has_any_role([User.ADMIN_ROLE, User.SALES_ROLE]):
                        bids = Bid.objects.filter(created_by__organization=request.user.organization)
                    else:
                        raise Exception("User is not authorized to view this page")
                else:
                    bids = Bid.objects.filter(created_by_id=request.user.id)
            else:
                raise Exception("User is not authorized to view this page")

            if bid_type == "in_progress":
                bids = bids.filter(is_accepted=True, is_rejected=False)
            elif bid_type == "completed":
                bids = bids.filter(is_accepted=True, is_rejected=False, status="completed")
            elif bid_type == "rejected":
                bids = bids.filter(is_rejected=True)
            elif bid_type == "pending":
                bids = bids.filter(is_accepted=False, is_rejected=False)

            if keyword:
                bids = bids.filter(task__title__icontains=keyword)

            bids = bids.filter(task__is_delete=False).order_by("-id")
            page = self.paginate_queryset(bids, request)
            serializer = BidSummarySerializer(page, many=True)
            count = bids.count()
            return Response({"data": serializer.data, "count": count})


class BidSummaryView(CRUDMixin):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "DELETE"]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @custom_exception_handler
    def get(self, request, ):
        bid_type = request.query_params.get('bid_type', None)
        keyword = request.query_params.get('keyword', None)
        if request.user.has_organization:
            if request.user.has_any_role([User.ADMIN_ROLE, User.TASK_MANAGER_ROLE]):
                tasks = Task.objects.filter(is_delete=False,
                                            origin_organization_id=request.user.organization).order_by(
                    "-id")
            else:
                raise Exception("User is not authorized to view this page")
        else:
            tasks = Task.objects.filter(is_delete=False, created_by_id=request.user.id).order_by(
                "-id")

        if bid_type == "in_progress":
            tasks = tasks.filter(is_accepted=True, is_completed=False)
        elif bid_type == "completed":
            tasks = tasks.filter(is_accepted=True, is_completed=True)
        elif bid_type == "pending":
            tasks = tasks.filter(is_accepted=False)
        if keyword:
            tasks = tasks.filter(title__icontains=keyword)
        tasks = tasks.filter(is_delete=False).order_by("-id")
        page = self.paginate_queryset(tasks, request)
        serializer = TaskBidSummarySerializer(page, many=True)
        count = tasks.count()
        return Response({"data": serializer.data, "count": count})


class BidManagementView(BaseView):
    permission_classes = [IsAuthenticated]
    serializer_class = BidManagementSerializer
    model = Bid

    @transaction.atomic
    @custom_exception_handler
    def put(self, request, object_id=None):
        instance = self.get_object(self.model, object_id)
        serializer = self.serializer_class(instance, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Successfully updated"})
