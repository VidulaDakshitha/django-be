from __future__ import unicode_literals

import base64
import secrets
import uuid
from datetime import datetime, timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db import transaction

from common.base_model import BaseModel
from core_apps.task.models import Skill
from core_apps.user.managers import UserManager
from utils.custom_datetime import get_formatted_current_time


class User(AbstractBaseUser, PermissionsMixin):
    ADMIN_ROLE = 'admin'
    CUSTOMER_ROLE = 'customer'
    CONSULTANT_MANAGER_ROLE = 'consultant_manager'
    TASK_MANAGER_ROLE = 'task_manager'
    CONSULTANT_ROLE = 'consultant'
    BILLING_ROLE = 'billing'
    SALES_ROLE = 'sales'
    GIG_WORKER_ROLE = 'gig_worker'
    OVER_EMPLOYEE_ROLE = 'over_employee'

    ORG_ROLES = [ADMIN_ROLE, CONSULTANT_MANAGER_ROLE, CONSULTANT_ROLE, BILLING_ROLE, SALES_ROLE]

    first_name = models.CharField(max_length=199, blank=True, null=True)
    last_name = models.CharField(max_length=199, blank=True, null=True)
    user_name = models.CharField(max_length=199, blank=True, null=True)
    chat_id = models.UUIDField(blank=True, null=True, unique=True)
    email = models.CharField(max_length=199, blank=True, null=True, unique=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    login_attempts = models.IntegerField(blank=True, null=True, default=0)
    reset_otp = models.CharField(max_length=100, null=True, blank=True)
    is_res_tok_valid = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=200, null=True, blank=True)
    res_tok_expire_date = models.CharField(max_length=200, null=True, blank=True)
    profile_image = models.FileField(upload_to='profile_image/', blank=True, null=True)
    is_face_id_verified = models.BooleanField(default=False)
    is_face_id_proceed = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_otp_sent = models.BooleanField(default=False)
    logged_on = models.CharField(max_length=200, blank=True, null=True)
    created_by_id = models.IntegerField(null=True, blank=True)
    created_on = models.CharField(max_length=200, null=True, blank=True)
    updated_by_id = models.IntegerField(null=True, blank=True)
    updated_on = models.CharField(max_length=200, null=True, blank=True)
    deleted_by_id = models.IntegerField(null=True, blank=True)
    deleted_on = models.CharField(max_length=200, null=True, blank=True)

    # Permission type fields
    is_super_admin = models.BooleanField(default=False)
    has_organization = models.BooleanField(default=False)
    roles = models.ManyToManyField("user.Role", related_name='user_roles', blank=True)

    skills = models.ManyToManyField(Skill, related_name='user_skill', blank=True)
    organization = models.ForeignKey("user.Organization", related_name="user_organization", on_delete=models.DO_NOTHING,
                                     null=True, blank=True)
    manager = models.ForeignKey("user.User", related_name="user_manager", on_delete=models.DO_NOTHING, null=True,
                                blank=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.id)

    def update(self, validated_data):
        if 'profile_pic' in validated_data:
            self.update_profile_image(validated_data['profile_pic'])
            validated_data.pop('profile_pic', None)

        for field, value in validated_data.items():
            setattr(self, field, value)
        self.save()

        return self

    def set_password_reset_token(self):
        self.is_res_tok_valid = True
        self.reset_token = secrets.token_urlsafe()
        self.res_tok_expire_date = str((datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"))
        self.save()

    def update_password(self, new_password):
        self.set_password(new_password)
        self.is_verified = True
        self.is_res_tok_valid = False
        self.save()

    def update_profile_image(self, profile_image):
        file_format, file_str = profile_image.split(';base64,')
        file_extension = file_format.split('/')[-1]

        file_data = base64.b64decode(file_str)

        self.profile_image = ContentFile(file_data, name=f'{secrets.token_hex(8)}.{file_extension}')
        self.save()

    def delete(self, **kwargs):
        self.deleted_on = get_formatted_current_time()
        self.is_delete = True
        self.save()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def set_roles(self, role_names):
        self.roles.clear()
        self._add_roles(role_names)

    def add_roles(self, role_names):
        self._add_roles(role_names)

    def _add_roles(self, role_names):
        for role_name in role_names:
            role = Role.objects.get(name=role_name)
            self.roles.add(role)

    def has_role(self, role_name):
        return self.roles.filter(name=role_name).exists()

    def has_any_role(self, role_names):
        return self.roles.filter(name__in=role_names).exists()

    def create_coworker(self):
        CoWorker.objects.create(
            user=self,
            organization=self.organization,
            manager=self.manager,
            is_accepted=True
        )


class Role(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)


class CoWorker(BaseModel):
    user = models.ForeignKey("user.User", related_name="user_co_worker", on_delete=models.DO_NOTHING,
                             null=True, blank=True)
    organization = models.ForeignKey("user.Organization", related_name="co_worker_organization",
                                     on_delete=models.DO_NOTHING,
                                     null=True, blank=True)
    manager = models.ForeignKey("user.User", related_name="co_worker_manager", on_delete=models.DO_NOTHING, null=True,
                                blank=True)
    is_external = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    token = models.CharField(max_length=255, null=True, blank=True)
    is_token_valid = models.BooleanField(default=False)

    def set_token(self):
        self.is_token_valid = True
        self.token = secrets.token_urlsafe()
        self.save()


class Organization(BaseModel):
    name = models.CharField(max_length=199, blank=True, null=True)
    url = models.CharField(max_length=199, blank=True, null=True)
    address_line1 = models.CharField(max_length=200, blank=True, null=True)
    address_line2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    zip_code = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=199, blank=True, null=True)
    logo = models.FileField(upload_to='organization_image/', blank=True, null=True)
    skills = models.ManyToManyField(Skill, related_name='organization_skill', blank=True)


class Language(BaseModel):
    user = models.ForeignKey("user.User", related_name="user_languages", on_delete=models.DO_NOTHING,
                             null=True, blank=True)
    language = models.ForeignKey("Locale", related_name="local_language", on_delete=models.DO_NOTHING, null=True,
                                 blank=True)
    expertise_level = models.CharField(max_length=199, blank=True, null=True)


class Awards(BaseModel):
    user = models.ForeignKey("user.User", related_name="user_awards", on_delete=models.DO_NOTHING, null=True,
                             blank=True)
    title = models.CharField(max_length=199, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    from_date = models.CharField(blank=True, null=True)
    to_date = models.CharField(blank=True, null=True)


class Certification(BaseModel):
    user = models.ForeignKey("user.User", related_name="user_certifications", on_delete=models.DO_NOTHING,
                             null=True, blank=True)
    title = models.CharField(max_length=199, blank=True, null=True)
    institution = models.CharField(max_length=199, blank=True, null=True)
    from_date = models.CharField(blank=True, null=True)
    to_date = models.CharField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)


class Locale(BaseModel):
    language = models.CharField(max_length=199, blank=True, null=True)
    symbol = models.CharField(max_length=199, blank=True, null=True)


class Project(BaseModel):
    user = models.ForeignKey("user.User", related_name="user_projects", on_delete=models.DO_NOTHING,
                             null=True, blank=True)
    title = models.CharField(max_length=199, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    from_date = models.CharField(blank=True, null=True)
    to_date = models.CharField(blank=True, null=True)


class Chatroom(BaseModel):
    init_user = models.ForeignKey("user.User", related_name="chat_room_init_user", on_delete=models.DO_NOTHING,
                                  null=True, blank=True)
    consumer = models.ForeignKey(User, related_name="chat_room_consumer", on_delete=models.DO_NOTHING,
                                 null=True, blank=True)
    chat_room_id = models.TextField(blank=True, null=True)
