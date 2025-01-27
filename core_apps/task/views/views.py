from datetime import datetime

from django.db.models import Count, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.base_permission import IsGigWorker, IsConsultant, IsOverEmployee, IsCustomer
from common.base_view import custom_exception_handler
from common.crud_mixin import CRUDMixin
from core_apps.task.models import Task
from core_apps.task.serializers.task_get_serializers import TaskRetrieveSerializer
from core_apps.task.serializers.task_serializers import TaskSerializer
from core_apps.user.models import User


class TaskView(CRUDMixin):
    permission_classes = [IsAuthenticated, (IsConsultant | IsGigWorker | IsOverEmployee | IsCustomer)]
    serializer_class = TaskSerializer
    model = Task


class TaskGetView(CRUDMixin):
    permission_classes = [IsAuthenticated, (IsConsultant | IsGigWorker | IsOverEmployee | IsCustomer)]
    serializer_class = TaskRetrieveSerializer
    model = Task
    http_method_names = ['get']

    @custom_exception_handler
    def get(self, request, object_id=None):
        if object_id:
            instance = self.get_object(self.model, object_id)
            serializer = TaskRetrieveSerializer(instance, many=False,
                                                context={'request': request, 'summary': False})
            return Response(serializer.data)
        else:
            keyword = request.query_params.get('keyword', None)
            job_type = request.query_params.get('job_type', None)
            experience = request.query_params.get('experience', None)
            min_bids = request.query_params.get('min_bids', None)
            max_bids = request.query_params.get('max_bids', None)
            summary = int(request.query_params.get('summary', 1))
            origin = request.query_params.get('origin', None)
            worker = request.query_params.get('worker', None)
            is_post_approved = request.query_params.get('is_post_approved', None)
            is_post_rejected = request.query_params.get('is_post_rejected', None)
            manager_assigned = request.query_params.get('manager_assigned', None)
            assignee_assigned = request.query_params.get('assignee_assigned', None)
            is_find_task = False
            if origin is not None and origin:
                if request.user.has_organization:
                    if request.user.has_any_role([User.ADMIN_ROLE, User.TASK_MANAGER_ROLE]):
                        instances = self.model.objects.filter(is_delete=False,
                                                              origin_organization_id=request.user.organization).order_by(
                            "-id")
                    else:
                        instances = self.model.objects.filter(is_delete=False,
                                                              created_by_id=request.user.id).order_by(
                            "-id")
                else:
                    instances = self.model.objects.filter(is_delete=False, created_by_id=request.user.id).order_by(
                        "-id")
            elif worker is not None and worker:
                if request.user.has_organization:
                    if request.user.has_any_role(
                            [User.ADMIN_ROLE, User.BILLING_ROLE, User.SALES_ROLE]):
                        instances = self.model.objects.filter(is_delete=False, is_accepted=True,
                                                              worker_organization_id=request.user.organization).order_by(
                            "-id")
                    elif request.user.has_any_role([User.CONSULTANT_MANAGER_ROLE]):
                        instances = self.model.objects.filter(is_delete=False, is_accepted=True,
                                                              # is_worker_accepted=True,
                                                              manager_id=request.user.id).order_by(
                            "-id")
                    else:
                        instances = self.model.objects.filter(is_delete=False, is_accepted=True,
                                                              # is_worker_accepted=True,
                                                              assignee_id=request.user.id).order_by(
                            "-id")
                else:
                    instances = self.model.objects.filter(is_delete=False, is_accepted=True,
                                                          assignee_id=request.user.id).order_by(
                        "-id")
            else:
                is_find_task = True
                if request.user.has_organization and request.user.has_any_role([User.ADMIN_ROLE, User.SALES_ROLE]):
                    # organization_skills = request.user.organization.skills.all()
                    instances = (self.model.objects.filter(
                        is_delete=False,
                        is_accepted=False,
                        is_post_approved=True,
                        bid_deadline__gte=datetime.now()
                        # ,
                        # skills__in=organization_skills
                    )
                                 .filter(
                        Q(is_sub_contractors_only=False) |
                        Q(is_sub_contractors_only=True, sub_organizations__in=[request.user.organization]))
                                 .exclude(
                        origin_organization=request.user.organization
                    ).distinct().order_by("-id"))
                else:
                    # user_skills = request.user.skills.all()
                    instances = (self.model.objects.filter(
                        is_delete=False,
                        is_accepted=False,
                        is_post_approved=True,
                        bid_deadline__gte=datetime.now(),
                        # skills__in=user_skills
                    ).exclude(created_by=request.user
                              ).filter(
                        Q(is_sub_contractors_only=False) |
                        Q(is_sub_contractors_only=True, sub_contractors__in=[request.user]))
                                 .distinct().order_by("-id"))

            if job_type:
                instances = instances.filter(job_type=job_type)

            if keyword:
                instances = instances.filter(title__icontains=keyword)

            if experience:
                instances = instances.filter(experience_level=experience)

            if max_bids:
                if not min_bids:
                    min_bids = 0

                instances = instances.annotate(bid_count=Count('bid')).filter(bid_count__gte=int(min_bids),
                                                                              bid_count__lte=int(max_bids))

            if is_post_approved is not None:
                instances = instances.filter(is_post_approved=is_post_approved)

            if is_post_rejected is not None:
                instances = instances.filter(is_post_rejected=is_post_rejected)

            if manager_assigned is not None:
                instances = instances.filter(manager__isnull=not bool(int(manager_assigned)))

            if assignee_assigned is not None:
                instances = instances.filter(assignee__isnull=not bool(int(assignee_assigned)))

            instances = instances.filter(is_delete=False).order_by("-id")
            page = self.paginate_queryset(instances, request)
            serializer = TaskRetrieveSerializer(page, many=True,
                                                context={'request': request, 'summary': summary,
                                                         'is_find_task': is_find_task})
            count = instances.count()
            return Response({"data": serializer.data, "count": count})
