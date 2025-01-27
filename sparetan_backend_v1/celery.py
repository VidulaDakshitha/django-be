# import os
#
# from celery import Celery
# from django.conf import settings
#
# # todo change this in dev
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sparetan_backend_v1.settings')
#
# app = Celery('sparetan_backend_v1')
#
# app.config_from_object('django.conf:settings', namespace='CELERY')
#
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
