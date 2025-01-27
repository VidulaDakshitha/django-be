from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        try:
            user_id = refresh.payload['user_id']
            user = User.objects.get(id=user_id)
        except (TokenError, User.DoesNotExist, KeyError):
            raise InvalidToken('Invalid token')

        try:
            refresh.blacklist()
        except AttributeError:
            pass

        new_refresh = RefreshToken.for_user(user)

        data = {
            'refresh': str(new_refresh),
            'access': str(new_refresh.access_token),
        }
        return data