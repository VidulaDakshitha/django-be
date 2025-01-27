from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, allow_blank=False)

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return value

    def validate(self, data):
        self.validate_password(data['password'])
        return data
