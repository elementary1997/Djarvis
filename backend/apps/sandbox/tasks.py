"""
Celery tasks for sandbox management.
"""
from celery import shared_task
from django.utils import timezone
import logging

from .models import SandboxSession
from .services import DockerExecutor

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_sandboxes():
    """
    Clean up expired sandbox containers.
    Runs every 5 minutes via Celery Beat.
    """
    logger.info("Starting sandbox cleanup task")
    
    # Find expired sessions
    expired_sessions = SandboxSession.objects.filter(
        status='running',
        expires_at__lt=timezone.now()
    )
    
    executor = DockerExecutor()
    cleaned = 0
    
    for session in expired_sessions:
        try:
            success = executor.stop_container(session.container_name)
            if success:
                session.status = 'expired'
                session.save(update_fields=['status'])
                cleaned += 1
                logger.info(f"Cleaned up expired sandbox: {session.container_name}")
        except Exception as e:
            logger.error(f"Failed to cleanup sandbox {session.container_name}: {e}")
    
    logger.info(f"Sandbox cleanup completed. Cleaned {cleaned} containers.")
    return cleaned
