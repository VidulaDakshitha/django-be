from datetime import datetime

from rest_framework import serializers

from common.base_serializer import CustomBaseSerializer
from core_apps.task.models import Task, Attachment, Skill
from core_apps.user.models import User
from utils.custom_datetime import naive_datetime, get_formatted_current_time


class TaskSerializer(CustomBaseSerializer):
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
    sub_organization_ids = serializers.ListField(
        child=serializers.JSONField(),
        write_only=True,
        required=False
    )
    manager_id = serializers.IntegerField(write_only=True, required=False)
    assignee_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'budget', 'currency', 'bid_type', 'bid_deadline', 'task_deadline',
            'acceptance_criteria', 'job_type', 'experience_level', 'files',
            'skills', 'required_skills',
            'sub_contractor_ids', 'sub_organization_ids', 'exit_criteria',
            'communication_deadline', 'communication_type', 'is_sub_contractors_only',
            'is_post_approved', 'manager_id', 'assignee_id'
        ]
        read_only_fields = ('is_delete',)

    def validate(self, data):
        if self.instance is None:
            required_fields = ['title', 'description', 'budget', 'currency', 'bid_type', 'bid_deadline',
                               'task_deadline', 'acceptance_criteria', 'job_type', 'experience_level']

            for field in required_fields:
                if field not in data or data[field] is [None, ""]:
                    raise serializers.ValidationError({"error": f"{field} is required and cannot be empty."})

            if naive_datetime(data['bid_deadline']) < datetime.now():
                raise serializers.ValidationError({"error": "Bid deadline cannot be in the past."})

            if naive_datetime(data['task_deadline']) < datetime.now():
                raise serializers.ValidationError({"error": "Task deadline cannot be in the past."})

            if naive_datetime(data['task_deadline']) < naive_datetime(data['bid_deadline']):
                raise serializers.ValidationError({"error": "Task deadline cannot be before bid deadline."})

            if data['budget'] < 0:
                raise serializers.ValidationError({"error": "Budget cannot be negative."})

            if data['bid_type'] not in ['open', 'closed']:
                raise serializers.ValidationError({"error": "Invalid bid type."})

        return data

    def create(self, validated_data):
        created_user = self.context['request'].user
        validated_data.update({
            "is_origin_organization": created_user.has_organization,
            "origin_organization": created_user.organization if created_user.has_organization else None,
            "is_post_approved": not created_user.has_organization,
            "task_owner": created_user if not created_user.has_organization else None,
            "post_approved_by": None if created_user.has_organization else created_user,
            "post_approved_on": None if created_user.has_organization else get_formatted_current_time(),
            "status": "pending",
            "created_by": created_user
        })

        attachments = validated_data.pop('files', [])
        skills = validated_data.pop('required_skills', [])
        sub_contractors = validated_data.pop('sub_contractor_ids', [])
        sub_organizations = validated_data.pop('sub_organization_ids', [])

        task = Task.objects.create(**validated_data)
        self.update_attachments(task, attachments, created_user)
        self.update_skills(task, skills)
        task.sub_contractors.set(sub_contractors)
        task.sub_organizations.set(sub_organizations)

        return task

    def update(self, instance, validated_data):
        updated_user = self.context['request'].user
        validated_data["updated_by"] = updated_user
        attachments = validated_data.pop('files', [])
        skills = validated_data.pop('required_skills', [])
        sub_contractors = validated_data.pop('sub_contractor_ids', [])
        sub_organizations = validated_data.pop('sub_organization_ids', [])

        is_post_approved = validated_data.pop("is_post_approved", None)
        if updated_user.has_any_role([User.ADMIN_ROLE, User.TASK_MANAGER_ROLE]):
            if is_post_approved is not None:
                validated_data["is_post_approved"] = is_post_approved
                validated_data["post_approved_by"] = updated_user
                validated_data["post_approved_on"] = get_formatted_current_time()

                if is_post_approved:
                    validated_data["task_owner"] = updated_user

        if updated_user.has_any_role([User.ADMIN_ROLE, User.SALES_ROLE]):
            manager_id = validated_data.pop('manager_id', None)
            if manager_id is not None:
                validated_data["manager"] = User.objects.get(id=manager_id)

        if updated_user.has_any_role([User.ADMIN_ROLE, User.CONSULTANT_MANAGER_ROLE]):
            assignee_id = validated_data.pop('assignee_id', None)
            if assignee_id is not None:
                validated_data["assignee"] = User.objects.get(id=assignee_id)

        instance = instance.update(validated_data)

        if sub_contractors:
            instance.sub_contractors.set(sub_contractors)

        if sub_organizations:
            instance.sub_organizations.set(sub_organizations)

        self.update_attachments(instance, attachments, updated_user)

        self.update_skills(instance, skills)

        return instance

    def update_attachments(self, instance, attachments, user):
        self.update_related_objects(instance, attachments, Attachment, 'task', user, required_decode=True)

    @staticmethod
    def update_skills(instance, skills):
        instance.skills.set(Skill.objects.filter(id__in=skills))
