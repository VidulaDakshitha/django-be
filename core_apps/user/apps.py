from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_apps.user'

    def ready(self):
        import core_apps.user.signals.user_signals  # Assuming your signals are defined here
