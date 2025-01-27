from celery import shared_task
from django.conf import settings

from utils.email_config import send_email


@shared_task
def send_forget_password_email(instance):
    try:
        send_email(instance.email, 'Forget Password', {"name": instance.first_name,
                                                       "link": f"{settings.WEB_URL}/register-confirm/{instance.id}/{instance.reset_token}"},
                   "change_password.html")
        return True
    except Exception as ex:
        print("Email failed to send " + str(ex))
        return False
