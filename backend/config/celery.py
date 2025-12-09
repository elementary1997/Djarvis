"""
Celery configuration for Djarvis project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('djarvis')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'cleanup-expired-sandboxes': {
        'task': 'apps.sandbox.tasks.cleanup_expired_sandboxes',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'cleanup-old-attempts': {
        'task': 'apps.exercises.tasks.cleanup_old_attempts',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')
