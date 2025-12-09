"""
Celery tasks for exercises.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import ExerciseAttempt

logger = logging.getLogger(__name__)


@shared_task
def cleanup_old_attempts():
    """
    Delete old exercise attempts (keep only last 10 per user/exercise).
    Runs daily at 2 AM via Celery Beat.
    """
    logger.info("Starting cleanup of old exercise attempts")
    
    from django.db.models import Count
    from apps.accounts.models import User
    
    deleted_count = 0
    
    for user in User.objects.all():
        for exercise_id in ExerciseAttempt.objects.filter(
            user=user
        ).values_list('exercise_id', flat=True).distinct():
            
            # Keep only last 10 attempts
            attempts = ExerciseAttempt.objects.filter(
                user=user,
                exercise_id=exercise_id
            ).order_by('-created_at')
            
            if attempts.count() > 10:
                old_attempts = attempts[10:]
                count = old_attempts.count()
                old_attempts.delete()
                deleted_count += count
    
    logger.info(f"Cleanup completed. Deleted {deleted_count} old attempts.")
    return deleted_count
