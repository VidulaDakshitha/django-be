import uuid

from django.conf import settings
from rest_framework import serializers
from rest_framework.fields import ListField

from common.base_serializer import CustomBaseSerializer
from core_apps.task.models import Skill
from core_apps.task.serializers.task_get_serializers import SkillSerializer
from core_apps.user.models import User, Organization, Language, Locale, Project, Certification
from core_apps.user.serializers.common_serializers import LanguageSerializer, CertificationSerializer, ProjectSerializer
from utils.custom_datetime import get_formatted_current_time
from utils.email_config import send_email


class OrganizationSerializer(CustomBaseSerializer):
    required_skills = ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'url', 'address_line1', 'address_line2', 'city', 'zip_code', 'country', 'description',
                  'logo', 'required_skills']
        read_only_fields = ('is_delete',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['skills'] = SkillSerializer(instance.skills.filter(is_delete=False), many=True).data
        return representation


class UserSerializer(CustomBaseSerializer):
    # update fields
    profile_pic = serializers.CharField(write_only=True, required=False)
    organization = OrganizationSerializer(required=False)
    required_skills = ListField(child=serializers.IntegerField(), write_only=True, required=False)
    languages = LanguageSerializer(many=True, required=False)
    certifications = CertificationSerializer(many=True, required=False)
    projects = ProjectSerializer(many=True, required=False)
    roles = ListField(child=serializers.CharField(), write_only=True, required=False)

    # validation fields
    has_completed_basic_details = serializers.SerializerMethodField()
    has_associated_organization_details = serializers.SerializerMethodField()
    has_skills = serializers.SerializerMethodField()
    has_languages = serializers.SerializerMethodField()
    available_roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'user_name', 'chat_id', 'email', 'country', 'phone_no',
                  'description',
                  'is_active', 'is_locked', 'is_face_id_verified', 'is_face_id_proceed', 'is_verified',
                  'is_super_admin', 'country', 'profile_pic',
                  'has_organization', 'organization', 'has_completed_basic_details',
                  'has_associated_organization_details', 'has_skills', 'has_languages', 'required_skills', 'languages',
                  'certifications', 'projects', 'available_roles', 'roles']
        read_only_fields = ('is_delete',)

    def validate(self, data):
        if self.instance is None:
            required_fields = ['first_name', 'last_name', 'email', 'roles']

            for field in required_fields:
                if field not in data or data[field] is [None, ""]:
                    raise serializers.ValidationError({"error": f"{field} is required and cannot be empty."})

            if User.objects.filter(email=data['email'], is_delete=False).exists():
                raise serializers.ValidationError({'email': 'Email already exists.'})

        else:
            if "user_name" in data and User.objects.filter(user_name=data['user_name']).exists():
                raise serializers.ValidationError({'user_name': 'User name already exists.'})

            if "email" in data and User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError({'email': 'Email already exists.'})

            if "phone_no" in data and User.objects.filter(phone_no=data['phone_no']).exists():
                raise serializers.ValidationError({'phone_no': 'Phone number already exists.'})

            if "user_name" in data and not data['user_name']:
                raise serializers.ValidationError({'user_name': 'User name cannot be empty.'})

            if "email" in data and not data['email']:
                raise serializers.ValidationError({'email': 'Email cannot be empty.'})

            if "phone_no" in data and not data['phone_no']:
                raise serializers.ValidationError({'phone_no': 'Phone number cannot be empty.'})

        return data

    def create(self, validated_data):
        roles = validated_data.pop('roles')
        roles.append(User.CUSTOMER_ROLE)
        created_user = self.context['request'].user
        validated_data['manager'] = created_user
        if created_user.has_organization:
            validated_data['has_organization'] = True
            validated_data['organization'] = created_user.organization

        user = User.objects.create(**validated_data)
        if user.has_organization:
            user.create_coworker()
        user.set_password_reset_token()
        user.created_on = get_formatted_current_time()
        user.chat_id = uuid.uuid4()
        user.set_roles(roles)
        user.save()

        self._send_verification_email(user, language=validated_data.get('language', 'en'))

        return user

    def update(self, instance, validated_data):
        validated_data["updated_by"] = self.context["request"].user

        if 'manager_id' in validated_data:
            manager_id = validated_data.pop('manager_id', None)
            manager_instance = User.objects.get(id=manager_id)
            instance.manager = manager_instance

        if instance.has_organization:
            organization_data = validated_data.pop('organization', None)

            if organization_data:
                if instance.organization:
                    organization_instance = instance.organization

                    if "required_skills" in organization_data:
                        org_skills = organization_data.pop('required_skills', None)
                        skills = Skill.objects.filter(id__in=org_skills)
                        organization_instance.skills.set(skills)

                    organization_instance.update(organization_data)
                else:
                    organization_instance = Organization.objects.create(**organization_data)
                    instance.organization = organization_instance

        if 'profile_pic' in validated_data:
            instance.update_profile_image(validated_data['profile_pic'])
            validated_data.pop('profile_pic', None)

        languages_data = validated_data.pop('locales', [])
        if languages_data:
            self.update_related_objects(instance, languages_data, Language, 'user',
                                        validated_data["updated_by"])

        skills_data = validated_data.pop('required_skills', [])
        if skills_data:
            skills = Skill.objects.filter(id__in=skills_data)
            instance.skills.set(skills)

        certifications_data = validated_data.pop('certifications', [])
        if certifications_data:
            self.update_related_objects(instance, certifications_data, Certification, 'user',
                                        validated_data["updated_by"])

        project_data = validated_data.pop('projects', [])
        if project_data:
            self.update_related_objects(instance, project_data, Project, 'user',
                                        validated_data["updated_by"])

        instance.update(validated_data)

        return instance

    @staticmethod
    def _send_verification_email(user, language):
        try:
            if language == "en":
                send_email(
                    user.email,
                    'Welcome to our platform',
                    {"name": user.first_name,
                     "link": f"{settings.WEB_URL}/register-confirm/{user.id}/{user.reset_token}"},
                    "user_verification.html"
                )
            elif language == "se":
                send_email(
                    user.email,
                    'Välkommen till vår plattform',
                    {"name": user.first_name,
                     "link": f"{settings.WEB_URL}/register-confirm/{user.id}/{user.reset_token}"},
                    "user_verification_se.html"
                )
        except Exception as ex:
            raise serializers.ValidationError({'email': 'Failed to send email'})

    @staticmethod
    def update_language(languages_data, updated_by, user_instance):
        if languages_data:
            for data in languages_data:
                obj_id = data.get('id')

                if obj_id:
                    try:
                        obj_instance = Language.objects.get(id=obj_id)
                        data["updated_by"] = updated_by
                        data["updated_on"] = get_formatted_current_time()

                        is_delete = data.pop("is_delete", False)
                        if is_delete:
                            obj_instance.delete(deleted_by=updated_by)
                            continue

                        if "language" in data:
                            data["language"] = Locale.objects.get(id=data["language"])

                        for attr, value in data.items():
                            setattr(obj_instance, attr, value)
                        obj_instance.save()
                    except Language.DoesNotExist:
                        continue
                else:
                    data["language"] = Locale.objects.get(id=data["language"])
                    data['user'] = user_instance
                    data['created_by'] = updated_by
                    Language.objects.get_or_create(**data)

    def get_has_completed_basic_details(self, obj):
        required_fields = [obj.user_name, obj.email, obj.country, obj.phone_no]
        return all(bool(field) for field in required_fields)

    def get_has_associated_organization_details(self, obj):
        if obj.has_organization and obj.organization:
            required_organization_fields = [
                obj.organization.name,
                obj.organization.url,
                obj.organization.address_line1,
                obj.organization.city,
                obj.organization.country
            ]
            return all(bool(field) for field in required_organization_fields)
        elif not obj.has_organization:
            return True
        return False

    def get_has_skills(self, obj):
        if obj.has_role(User.GIG_WORKER_ROLE) or obj.has_role(User.OVER_EMPLOYEE_ROLE) or obj.has_role(
                User.CONSULTANT_ROLE):
            return obj.skills.exists()
        return True

    def get_has_languages(self, obj):
        if obj.has_role(User.GIG_WORKER_ROLE) or obj.has_role(User.OVER_EMPLOYEE_ROLE) or obj.has_role(
                User.CONSULTANT_ROLE):
            return obj.user_languages.exists()
        return True

    def get_available_roles(self, obj):
        return [role.name for role in obj.roles.all()]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['manager_id'] = instance.manager_id if instance.manager else ""
        representation['manager_name'] = instance.manager.get_full_name() if instance.manager else ""
        representation['skills'] = SkillSerializer(instance.skills.filter(is_delete=False), many=True).data
        representation['languages'] = LanguageSerializer(instance.user_languages.filter(is_delete=False),
                                                         many=True).data
        representation['projects'] = ProjectSerializer(instance.user_projects.filter(is_delete=False), many=True).data
        representation['certifications'] = CertificationSerializer(
            instance.user_certifications.filter(is_delete=False), many=True
        ).data

        return representation


class UserSummarySerializer(CustomBaseSerializer):
    # update fields
    has_completed_basic_details = serializers.SerializerMethodField()
    has_associated_organization_details = serializers.SerializerMethodField()
    has_skills = serializers.SerializerMethodField()
    has_languages = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    is_external = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'chat_id', 'email', 'country', 'phone_no',
                  'is_active', 'is_locked', 'is_face_id_verified', 'is_face_id_proceed', 'is_verified',
                  'has_completed_basic_details', 'has_organization',
                  'has_associated_organization_details', 'has_skills', 'has_languages', 'roles', 'is_external']
        read_only_fields = ('is_delete',)

    def get_has_completed_basic_details(self, obj):
        required_fields = [obj.user_name, obj.email, obj.country, obj.phone_no]
        return all(bool(field) for field in required_fields)

    def get_has_associated_organization_details(self, obj):
        if obj.has_organization and obj.organization:
            required_organization_fields = [
                obj.organization.name,
                obj.organization.url,
                obj.organization.address_line1,
                obj.organization.city,
                obj.organization.country
            ]
            return all(bool(field) for field in required_organization_fields)
        elif not obj.has_organization:
            return True
        return False

    def get_has_skills(self, obj):
        if obj.has_role(User.GIG_WORKER_ROLE) or obj.has_role(User.OVER_EMPLOYEE_ROLE) or obj.has_role(
                User.CONSULTANT_ROLE):
            return obj.skills.exists()
        return True

    def get_has_languages(self, obj):
        if obj.has_role(User.GIG_WORKER_ROLE) or obj.has_role(User.OVER_EMPLOYEE_ROLE) or obj.has_role(
                User.CONSULTANT_ROLE):
            return obj.user_languages.exists()
        return True

    def get_roles(self, obj):
        return [role.name for role in obj.roles.all()]

    def get_is_external(self, obj):
        return 0 if obj.organization else 1

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['manager_id'] = instance.manager_id if instance.manager else ""
        representation['manager_name'] = instance.manager.get_full_name() if instance.manager else ""

        return representation
