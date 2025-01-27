from rest_framework import serializers

from django.conf import settings
from rest_framework import serializers

from common.base_serializer import CustomBaseSerializer
from core_apps.bid.models import Bid
from core_apps.task.models import Task, Attachment, Skill
from core_apps.user.models import User
from core_apps.user.serializers.common_serializers import OrganizationIdNameSerializer, UserIdNameSerializer


class SkillSerializer(CustomBaseSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'skill']


class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'file_url', 'name']

    def get_file_url(self, obj):
        request = self.context.get('request')
        be_url = settings.BACKEND_URL
        file_url = request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return f"{be_url}{file_url}" if be_url else file_url


class TaskRetrieveSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    required_skills = serializers.ListField(
        child=serializers.JSONField(),
        write_only=True,
        required=False
    )
    files = serializers.ListField(
        child=serializers.JSONField(),
        write_only=True,
        required=False
    )
    sub_contractor_ids = serializers.ListField(
        child=serializers.JSONField(),
        write_only=True,
        required=False
    )
    min_bid_value = serializers.SerializerMethodField()
    max_bid_value = serializers.SerializerMethodField()
    origin_organization = OrganizationIdNameSerializer(read_only=True)
    manage_organization = OrganizationIdNameSerializer(read_only=True)
    post_approved_by = UserIdNameSerializer(read_only=True)
    assignee = UserIdNameSerializer(read_only=True)
    manager = UserIdNameSerializer(read_only=True)
    post_status = serializers.SerializerMethodField()
    has_manager = serializers.SerializerMethodField()
    has_assignee = serializers.SerializerMethodField()
    task_status = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'budget', 'currency', 'bid_type', 'bid_deadline', 'task_deadline',
            'acceptance_criteria', 'created_by', 'job_type', 'experience_level', 'attachments', 'files',
            'skills', 'is_completed', 'is_accepted', 'status', 'required_skills', 'created_on',
            'updated_on', 'updated_by', 'min_bid_value', 'max_bid_value', 'sub_contractor_ids', 'sub_contractors',
            'total_amount', 'remaining_amount', 'is_fully_paid', 'progress', 'exit_criteria',
            'communication_deadline', 'communication_type', 'is_sub_contractors_only',
            'is_origin_organization', 'origin_organization', 'is_post_approved', 'is_post_rejected', 'post_approved_by',
            'post_approved_on', 'is_worker_organization', 'manage_organization', 'assignee', 'manager', 'post_status',
            'has_manager', 'has_assignee', 'task_status', 'is_worker_accepted'
        ]
        read_only_fields = ('is_delete',)

    def __init__(self, *args, **kwargs):
        summary = kwargs.get('context', {}).pop('summary', False)
        is_find_task = kwargs.get('context', {}).pop('is_find_task', False)
        super(TaskRetrieveSerializer, self).__init__(*args, **kwargs)

        user = self.context.get('request').user if self.context.get('request') else None
        if is_find_task:
            summary_fields = ['id', 'title', 'budget', 'currency', 'description', 'bid_deadline',
                              'task_deadline', 'skills']
            for field_name in set(self.fields.keys()) - set(summary_fields):
                self.fields.pop(field_name)
        else:
            if user and user.is_authenticated:
                if user.has_any_role([User.ADMIN_ROLE, User.TASK_MANAGER_ROLE]):
                    if summary:
                        summary_fields = ['id', 'title', 'budget', 'currency', 'bid_deadline',
                                          'is_accepted', 'is_worker_accepted', 'task_status',
                                          'created_on', 'post_status', 'has_manager', 'has_assignee', 'exit_criteria']
                        for field_name in set(self.fields.keys()) - set(summary_fields):
                            self.fields.pop(field_name)
                elif user.has_any_role([User.SALES_ROLE]):
                    if summary:
                        summary_fields = ['id', 'title', 'budget', 'currency', 'bid_type', 'bid_deadline',
                                          'task_status',
                                          'task_deadline', 'is_completed', 'has_manager', 'created_on', 'is_accepted',
                                          'is_worker_accepted', 'exit_criteria']
                        for field_name in set(self.fields.keys()) - set(summary_fields):
                            self.fields.pop(field_name)
                elif user.has_any_role([User.CONSULTANT_MANAGER_ROLE]):
                    if summary:
                        summary_fields = ['id', 'title', 'task_status',
                                          'task_deadline', 'is_completed', 'has_assignee', 'created_on']
                        for field_name in set(self.fields.keys()) - set(summary_fields):
                            self.fields.pop(field_name)
                elif user.has_any_role([User.CONSULTANT_ROLE]):
                    if summary:
                        summary_fields = ['id', 'title', 'task_status',
                                          'task_deadline', 'is_completed', 'has_assignee', 'created_on']
                        for field_name in set(self.fields.keys()) - set(summary_fields):
                            self.fields.pop(field_name)
                else:
                    if summary:
                        summary_fields = ['id', 'title', 'budget', 'currency', 'bid_type', 'bid_deadline',
                                          'task_deadline', 'is_completed', 'task_status', 'created_on']
                        for field_name in set(self.fields.keys()) - set(summary_fields):
                            self.fields.pop(field_name)

    def get_min_bid_value(self, obj):
        return Bid.objects.filter(task=obj).order_by('amount').values_list('amount', flat=True).first() or "0.00"

    def get_max_bid_value(self, obj):
        return Bid.objects.filter(task=obj).order_by('-amount').values_list('amount', flat=True).first() or "0.00"

    def get_post_status(self, obj):
        if obj.is_post_approved:
            return "Approved"
        elif obj.is_post_rejected:
            return "is_accepted"
        else:
            return "Pending"

    def get_task_status(self, obj):
        if obj.is_completed:
            return "Completed"
        elif obj.is_worker_accepted:
            return "In Progress"
        elif obj.is_accepted and not obj.is_worker_accepted:
            return "Awaiting Acceptance"
        else:
            return "Pending"

    def get_has_manager(self, obj):
        return obj.manager is not None

    def get_has_assignee(self, obj):
        return obj.assignee is not None


class TaskIdNameSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'skills']
