"""
Celery configuration for Djarvis project.

Обрабатывает асинхронное выполнение Ansible playbooks и управление контейнерами.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('djarvis')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task для проверки работы Celery."""
    print(f'Request: {self.request!r}')
