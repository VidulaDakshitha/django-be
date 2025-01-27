import base64
import secrets

from django.core.files.base import ContentFile
from django.db import models

from utils.custom_datetime import get_formatted_current_time


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "user.User", related_name='created_%(class)s_set', on_delete=models.DO_NOTHING, null=True, blank=True
    )
    created_on = models.CharField(max_length=100, null=True, blank=True)
    updated_by = models.ForeignKey(
        "user.User", related_name='updated_%(class)s_set', on_delete=models.DO_NOTHING, null=True, blank=True
    )
    updated_on = models.CharField(max_length=100, null=True, blank=True)
    deleted_by = models.ForeignKey(
        "user.User", related_name='deleted_%(class)s_set', on_delete=models.DO_NOTHING, null=True, blank=True
    )
    deleted_on = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.created_on:
            self.created_on = get_formatted_current_time()
        super(BaseModel, self).save(*args, **kwargs)

    def update(self, validated_data):
        validated_data.pop('is_delete', None)

        for field, value in validated_data.items():
            setattr(self, field, value)

        self.updated_on = get_formatted_current_time()
        self.updated_by = validated_data.get('updated_by', None)
        self.save()

        return self

    def delete(self, **kwargs):
        self.deleted_by = kwargs.get('deleted_by', None)
        self.deleted_on = get_formatted_current_time()
        self.is_delete = True
        self.save()

    def get_user_full_name(self, user):
        if user:
            return f"{user.first_name} {user.last_name}".strip()
        return ""

    def get_created_user(self):
        return self.get_user_full_name(self.created_by)

    def get_updated_user(self):
        return self.get_user_full_name(self.updated_by)
