import uuid

from django.conf import settings
from rest_framework import serializers

from common.base_serializer import CustomBaseSerializer
from core_apps.user.models import User, Organization, CoWorker
from utils.custom_datetime import get_formatted_current_time
from utils.email_config import send_email


class RegisterSerializer(CustomBaseSerializer):
    user_type = serializers.CharField(required=True)
    organization_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'country', 'user_type', 'organization_name']

    def validate(self, data):
        required_fields = ['first_name', 'last_name', 'email']

        for field in required_fields:
            if field not in data or data[field] is [None, ""]:
                raise serializers.ValidationError({"error": f"{field} is required and cannot be empty."})

        if User.objects.filter(email=data['email'], is_delete=False).exists():
            raise serializers.ValidationError({'email': 'Email already exists.'})

        return data

    def create(self, validated_data):
        validated_data = self._process_type(validated_data)
        roles = validated_data.pop('roles')
        user = User.objects.create(**validated_data)
        user.set_password_reset_token()
        user.created_on = get_formatted_current_time()
        user.chat_id = uuid.uuid4()
        user.save()
        user.set_roles(roles)

        if user.has_organization:
            user.create_coworker()
        self._send_verification_email(user)

        return user

    @staticmethod
    def _process_type(validated_data):
        user_type = validated_data.pop('user_type')

        if user_type == "OR":
            validated_data['has_organization'] = True
            organization_name = validated_data.pop('organization_name')
            validated_data['organization'] = Organization.objects.create(name=organization_name,
                                                                         country=validated_data['country'])
            validated_data["roles"] = [User.ADMIN_ROLE]
        elif user_type == "GW":
            validated_data["roles"] = [User.CUSTOMER_ROLE, User.GIG_WORKER_ROLE]
        elif user_type == "OE":
            validated_data["roles"] = [User.CUSTOMER_ROLE, User.OVER_EMPLOYEE_ROLE]
        else:
            validated_data["roles"] = [User.CUSTOMER_ROLE]

        return validated_data

    @staticmethod
    def _send_verification_email(user):
        try:
            send_email(
                user.email,
                'Welcome to our platform',
                {"name": user.first_name, "link": f"{settings.WEB_URL}/register-confirm/{user.id}/{user.reset_token}"},
                "user_verification.html"
            )
        except Exception as ex:
            raise serializers.ValidationError({'email': 'Failed to send email'})
