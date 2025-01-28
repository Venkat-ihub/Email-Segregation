# my_app/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import multiprocessing
if os.name == 'nt':  # Check if the operating system is Windows
    multiprocessing.set_start_method('spawn')
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_app.settings')

app = Celery('my_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()  # Automatically discover tasks in installed apps
