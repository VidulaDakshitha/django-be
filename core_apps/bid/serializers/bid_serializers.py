from rest_framework import serializers

from common.base_serializer import CustomBaseSerializer
from core_apps.task.models import Task
from core_apps.bid.models import Bid, AdditionalCost
from core_apps.task.serializers.task_get_serializers import TaskIdNameSerializer
from utils.custom_datetime import get_formatted_current_time


class AdditionalCostSerializer(CustomBaseSerializer):
    class Meta:
        model = AdditionalCost
        fields = ['id', 'cost', 'description', 'currency', 'is_active', 'created_by', 'created_on', 'updated_by',
                  'updated_on']
        read_only_fields = ('is_delete',)


class BidSerializer(CustomBaseSerializer):
    task_id = serializers.IntegerField(write_only=True)
    task = TaskIdNameSerializer(read_only=True)
    additional_costs = AdditionalCostSerializer(many=True, read_only=True)
    costs = serializers.ListField(
        child=serializers.JSONField(),
        write_only=True,
        required=False
    )
    bidder_id = serializers.CharField(source='bidder.id', read_only=True)
    employer_id = serializers.CharField(source='employer.id', read_only=True)
    bidder_name = serializers.SerializerMethodField()
    employer_name = serializers.SerializerMethodField()
    bid_status = serializers.SerializerMethodField()

    class Meta:
        model = Bid
        fields = ['id', 'task', 'amount', 'currency', 'description', 'message', 'revision',
                  'cover_letter',
                  'is_accepted', 'is_rejected', 'is_active', 'created_by', 'created_on', 'updated_by',
                  'updated_on', 'task_id', 'bid_updated_on', 'bid_updated_by', 'additional_costs', 'costs',
                  'bidder_id', 'employer_id', 'bidder_name', 'employer_name', 'bid_status']
        read_only_fields = ('is_delete',)

    def validate(self, data):
        if self.instance is None:
            required_fields = ['task_id', 'amount', 'currency', 'description', 'message', 'revision',
                               'cover_letter']

            for field in required_fields:
                if field not in data or data[field] is [None, ""]:
                    raise serializers.ValidationError({"error": f"{field} is required and cannot be empty."})

            if not Task.objects.filter(id=data['task_id']).exists():
                raise serializers.ValidationError({"error": "Invalid task id."})

            if data['amount'] <= 0:
                raise serializers.ValidationError({"error": "Invalid amount."})

            if data['currency'] not in ['USD', 'EUR', 'GBP', 'INR', 'SEK']:
                raise serializers.ValidationError({"error": "Invalid currency."})

            if Bid.objects.filter(task_id=data['task_id'],
                                  bidder_id=self.context['request'].user.id).exists():
                raise serializers.ValidationError({"error": "You have already placed a bid for this task."})

        else:
            if self.instance.is_accepted:
                raise serializers.ValidationError({"error": "Bid has already been accepted."})

            if self.instance.is_rejected:
                raise serializers.ValidationError({"error": "Bid has already been rejected."})

            if self.instance.is_completed:
                raise serializers.ValidationError({"error": "Bid has already been completed."})

            if self.instance.task.is_accepted:
                raise serializers.ValidationError({"error": "Task has already been accepted."})

        return data

    def create(self, validated_data):
        task = Task.objects.get(id=validated_data.pop('task_id'))
        costs = validated_data.pop('costs', [])
        validated_data['task'] = task
        validated_data['created_by'] = self.context['request'].user
        validated_data['bidder'] = self.context['request'].user
        validated_data['employer'] = task.task_owner if task.task_owner else task.created_by
        validated_data['status'] = "pending"
        bid = Bid.objects.create(**validated_data)

        self.update_additional_cost(bid, costs, self.context['request'].user)
        return bid

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        costs = validated_data.pop('additional_costs', [])
        self.update_additional_cost(instance, costs, self.context['request'].user)
        return instance.update(validated_data)

    def update_additional_cost(self, instance, costs, user):
        self.update_related_objects(instance, costs, AdditionalCost, 'bid', user)

    def get_bidder_name(self, obj):
        if obj.bidder.has_organization:
            return obj.bidder.organization.name
        return f"{obj.bidder.first_name} {obj.bidder.last_name}".strip()

    def get_employer_name(self, obj):
        if obj.task.is_origin_organization:
            return obj.task.origin_organization.name
        return f"{obj.task.created_by.first_name} {obj.task.created_by.last_name}".strip()

    def get_bid_status(self, obj):
        if obj.is_accepted:
            return "Approved"
        elif obj.is_rejected:
            return "Rejected"
        else:
            return "Pending"


class BidManagementSerializer(CustomBaseSerializer):
    is_accepted = serializers.BooleanField(write_only=True, required=True)

    class Meta:
        model = Bid
        fields = ['is_accepted']

    def validate(self, data):
        if self.instance:
            if self.instance.is_accepted:
                raise serializers.ValidationError({"error": "Bid has already been accepted."})

            if self.instance.is_rejected:
                raise serializers.ValidationError({"error": "Bid has already been rejected."})

            if self.instance.task.is_accepted:
                raise serializers.ValidationError({"error": "Task has already been accepted."})

        return data

    def update(self, instance, validated_data):
        if validated_data['is_accepted']:
            instance.task.is_accepted = True
            instance.task.assignee = instance.bidder
            instance.task.total_amount = instance.amount
            instance.task.remaining_amount = instance.amount
            instance.task.is_worker_organization = 1 if instance.bidder.has_organization else 0
            instance.task.worker_organization = instance.bidder.organization if instance.bidder.has_organization else None
            instance.task.save()

            instance.is_accepted = True
            instance.bid_updated_on = get_formatted_current_time()
            instance.bid_updated_by = self.context['request'].user
            instance.save()

            bids = Bid.objects.filter(task=instance.task).exclude(id=instance.id)
            bids.update(is_rejected=True)

        else:
            instance.is_rejected = True
            instance.save()

        return instance


class BidSummarySerializer(CustomBaseSerializer):
    task_id = serializers.IntegerField(source='task.id', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    bidder_name = serializers.SerializerMethodField()
    employer_name = serializers.SerializerMethodField()
    bid_status = serializers.SerializerMethodField()

    class Meta:
        model = Bid
        fields = ['id', 'task_id', 'task_title', 'amount', 'currency',
                  'is_accepted', 'is_rejected', 'bidder_name', 'employer_name', 'bid_status']

    def get_bidder_name(self, obj):
        if obj.bidder.has_organization:
            return obj.bidder.organization.name
        return f"{obj.bidder.first_name} {obj.bidder.last_name}".strip()

    def get_employer_name(self, obj):
        if obj.task.is_origin_organization:
            return obj.task.origin_organization.name
        return f"{obj.task.created_by.first_name} {obj.task.created_by.last_name}".strip()

    def get_bid_status(self, obj):
        if obj.is_accepted:
            return "Approved"
        elif obj.is_rejected:
            return "Rejected"
        else:
            return "Pending"

    # def __init__(self, *args, **kwargs):
    #     origin = kwargs.get('context', {}).pop('origin', None)
    #     worker = kwargs.get('context', {}).pop('worker', None)
    #     super(BidSummarySerializer, self).__init__(*args, **kwargs)

    #     if origin is not None and origin:
    #         required_fields = ['id', 'task_id', 'task_title', 'amount', 'currency',
    #                            'is_accepted', 'is_rejected', 'bidder_name', 'employer_name', 'status']
    #         for field_name in set(self.fields.keys()) - set(required_fields):
    #             self.fields.pop(field_name)
