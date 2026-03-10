


import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Fitness_Club.settings')

app = Celery('Fitness_Club')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()