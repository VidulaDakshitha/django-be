from rest_framework import serializers

from common.base_serializer import CustomBaseSerializer
from core_apps.user.models import Language, Awards, Certification, Locale, Project, User, Organization


class LocaleSerializer(CustomBaseSerializer):
    class Meta:
        model = Locale
        fields = ['id', 'language', 'symbol']


class LanguageSerializer(CustomBaseSerializer):
    language = LocaleSerializer()

    class Meta:
        model = Language
        fields = ['id', 'language', 'expertise_level', 'is_delete']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['language_id'] = representation['language']['id'] if representation['language'] else 0
        representation['language'] = representation['language']['language'] if representation['language'] else ""
        return representation


class AwardSerializer(CustomBaseSerializer):
    class Meta:
        model = Awards
        fields = ['id', 'title', 'description', 'from_date', 'to_date', 'is_active', 'is_delete']


class CertificationSerializer(CustomBaseSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Certification
        fields = ['id', 'title', 'institution', 'description', 'from_date', 'to_date', 'is_active', 'is_delete']


class ProjectSerializer(CustomBaseSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'from_date', 'to_date', 'is_active', 'is_delete']


class UserIdNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = f"{instance.first_name} {instance.last_name}".strip()
        return representation


class OrganizationIdNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name']
