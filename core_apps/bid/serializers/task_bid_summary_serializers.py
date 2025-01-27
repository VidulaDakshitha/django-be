from rest_framework import serializers

from django.conf import settings
from rest_framework import serializers

from common.base_serializer import CustomBaseSerializer
from core_apps.bid.models import Bid
from core_apps.task.models import Task, Attachment, Skill
from core_apps.user.models import User
from core_apps.user.serializers.common_serializers import OrganizationIdNameSerializer, UserIdNameSerializer


class TaskBidSummarySerializer(serializers.ModelSerializer):
    min_bid_value = serializers.SerializerMethodField()
    max_bid_value = serializers.SerializerMethodField()
    bid_status = serializers.SerializerMethodField()
    bid_count = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'budget', 'currency', 'bid_deadline', 'bid_status', 'min_bid_value', 'max_bid_value', 'bid_count'
        ]
        read_only_fields = ('is_delete',)

    def get_min_bid_value(self, obj):
        return Bid.objects.filter(task=obj).order_by('amount').values_list('amount', flat=True).first() or "0.00"

    def get_max_bid_value(self, obj):
        return Bid.objects.filter(task=obj).order_by('-amount').values_list('amount', flat=True).first() or "0.00"
    
    def get_bid_status(self, obj):
        if obj.is_accepted:
            if obj.is_completed:
                return "Completed"
            else:
                return "In Progress"
        else:
            return "Pending"
        
    def get_bid_count(self, obj):
        return Bid.objects.filter(task=obj).count()
