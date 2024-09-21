import os
from celery import Celery
from time import sleep

os.environ.setdefault('DJANGO_SETTINGS_MODULE','news_reader.settings')

app = Celery('news_reader')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()