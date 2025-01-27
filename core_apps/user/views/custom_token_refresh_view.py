from rest_framework_simplejwt.views import TokenRefreshView

from core_apps.user.serializers.custom_token_refresh_serializer import CustomTokenRefreshSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
