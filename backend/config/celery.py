"""
Celery configuration for Djarvis project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('djarvis')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Periodic tasks schedule
app.conf.beat_schedule = {
    'cleanup-expired-sandboxes': {
        'task': 'apps.sandbox.tasks.cleanup_expired_sandboxes',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'cleanup-old-execution-results': {
        'task': 'apps.sandbox.tasks.cleanup_old_execution_results',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')
