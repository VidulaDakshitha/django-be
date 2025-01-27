import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from core_apps.user.models import User
from utils.custom_datetime import get_formatted_current_time


def handle_user_post_save(user_id):
    pass
    # user = User.objects.get(pk=user_id)
    # user.set_password_reset_token()
    # user.created_on = get_formatted_current_time()
    # user.chat_id = uuid.uuid4()
    # user.save()


@receiver(post_save, sender=User)
def user_post_save_handler(sender, instance, created, **kwargs):
    if created:
        handle_user_post_save(instance.id)
