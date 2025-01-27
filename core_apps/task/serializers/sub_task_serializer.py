from datetime import datetime

from django.conf import settings
from rest_framework import serializers

from common.base_serializer import CustomBaseSerializer
from core_apps.task.models import SubTask, SubtaskFile, Task, Invoice


class SubmissionFileSerializer(CustomBaseSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = SubtaskFile
        fields = ['id', 'file', 'name', 'file_url']
        read_only_fields = ('is_delete',)

    def get_file_url(self, obj):
        request = self.context.get('request')
        be_url = settings.BACKEND_URL
        file_url = request.build_absolute_uri(obj.file.url) if request else obj.file.url
        if be_url:
            return be_url + file_url
        return file_url


class InvoiceFileSerializer(CustomBaseSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'file', 'amount', 'is_accepted', 'is_rejected', 'is_paid', 'date_paid']
        read_only_fields = ('is_delete',)


class SubTaskSerializer(CustomBaseSerializer):
    files = serializers.ListField(
        child=serializers.JSONField(),
        write_only=True,
        required=False
    )
    invoices = serializers.ListField(
        child=serializers.JSONField(),
        write_only=True,
        required=False
    )
    subtask_files = SubmissionFileSerializer(many=True, read_only=True)
    task_id = serializers.IntegerField(write_only=True)
    sub_task_invoice = InvoiceFileSerializer(many=True, read_only=True)

    class Meta:
        model = SubTask
        fields = ['id', 'task_id', 'description', 'from_date', 'to_date', 'time_logged', 'is_completed',
                  'revision', 'is_invoiced', 'is_paid', 'is_active', 'created_by', 'created_on', 'updated_by',
                  'updated_on', 'files', 'subtask_files', 'invoices', 'sub_task_invoice']
        read_only_fields = ('is_delete',)

    def validate(self, data):
        if self.instance is None:
            required_fields = ['task_id', 'description', 'from_date', 'to_date']

            for field in required_fields:
                if field not in data or data[field] in [None, ""]:
                    raise serializers.ValidationError({"error": f"{field} is required and cannot be empty."})

            if Task.objects.filter(id=data['task_id'], is_completed=True).exists():
                raise serializers.ValidationError({"error": "Task has already been completed."})

        return data

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        invoices = validated_data.pop('invoices', [])
        task_id = validated_data.pop('task_id')
        validated_data['task'] = Task.objects.get(id=task_id)
        validated_data['time_logged'] = self.get_time_difference(validated_data['from_date'], validated_data['to_date'])
        validated_data['created_by'] = self.context['request'].user
        subtask = SubTask.objects.create(**validated_data)
        self.update_files(subtask, files, self.context['request'].user)

        if invoices:
            processed_invoices = self.process_invoices(subtask, invoices)
            self.update_invoices(subtask, processed_invoices, self.context['request'].user)
            
        return subtask

    def update(self, instance, validated_data):
        invoices = validated_data.pop('invoices', [])
        
        validated_data['updated_by'] = self.context['request'].user
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if invoices:
            processed_invoices = self.process_invoices(instance, invoices)
            self.update_invoices(instance, processed_invoices, self.context['request'].user)
        
        return instance

    def update_files(self, instance, files, user):
        self.update_related_objects(instance, files, SubtaskFile, 'subtask', user, required_decode=True)

    def update_invoices(self, instance, invoices, user):
        self.update_related_objects(instance, invoices, Invoice, 'subtask', user, required_decode=True)

    def process_invoices(self, instance, invoices):
        for invoice in invoices:
            invoice['assignee'] = instance.created_by
            invoice['client'] = instance.task.created_by

        return invoices

    @staticmethod
    def get_time_difference(from_date, to_date):
        if from_date and to_date:
            from_date = datetime.strptime(from_date, "%Y-%m-%d %H:%M:%S")
            to_date = datetime.strptime(to_date, "%Y-%m-%d %H:%M:%S")

            time_difference = to_date - from_date
            total_seconds_difference = time_difference.total_seconds()
            hours_difference = total_seconds_difference / 3600
            return hours_difference
        else:
            return None
