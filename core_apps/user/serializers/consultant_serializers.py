from django.conf import settings
from rest_framework import serializers

from common.base_serializer import CustomBaseSerializer

from core_apps.user.models import User, CoWorker
from utils.email_config import send_email


class ConsultantSerializer(CustomBaseSerializer):
    consultant_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CoWorker
        fields = ['consultant_id']
        read_only_fields = ('is_delete',)

    def validate(self, data):
        if self.instance is None:
            required_fields = ['consultant_id']

            for field in required_fields:
                if field not in data or data[field] in [None, ""]:
                    raise serializers.ValidationError({"error": f"{field} is required and cannot be empty."})

            if CoWorker.objects.filter(user_id=data['consultant_id'],
                                       organization=self.context['request'].user.organization).exists():
                raise serializers.ValidationError({"error": "Consultant already exists."})

        return data

    def create(self, validated_data):
        created_user = self.context['request'].user
        manager = created_user
        organization = created_user.organization
        user_id = validated_data.pop('consultant_id')
        user = User.objects.get(id=user_id)

        consultant = CoWorker.objects.create(
            user=user,
            organization=organization,
            is_accepted=False,
            is_external=True,
            manager=manager
        )
        consultant.set_token()
        self._send_verification_email(consultant, language=validated_data.get("language", "en"))

        return consultant

    @staticmethod
    def _send_verification_email(connection, language):
        try:
            if language == "en":
                send_email(
                    connection.user.email,
                    f"Invitation to Connect with {connection.organization.name} ",
                    {"name": connection.user.first_name,
                     "link": f"{settings.WEB_URL}/connection-accept/{connection.id}/{connection.token}",
                     "organization_name": connection.organization.name
                     },
                    "connection_accept.html"
                )
            elif language == "se":
                send_email(
                    connection.user.email,
                    f"Inbjudan att ansluta till {connection.organization.name} ",
                    {"name": connection.user.first_name,
                     "link": f"{settings.WEB_URL}/connection-accept/{connection.id}/{connection.token}",
                     "organization_name": connection.organization.name
                     },
                    "connection_accept_se.html"
                )
        except Exception as ex:
            raise serializers.ValidationError({'email': 'Failed to send email'})
