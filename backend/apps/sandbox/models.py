"""
Models for sandbox execution sessions.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SandboxSession(models.Model):
    """
    Tracks active sandbox containers for students.
    
    Attributes:
        user: Student using the sandbox
        container_id: Docker container ID
        container_name: Unique container name
        status: Current status (starting, running, stopped, error)
        created_at: When session was created
        expires_at: When session should be cleaned up
        last_activity: Last time container was used
    """
    
    STATUS_CHOICES = [
        ('starting', 'Starting'),
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('error', 'Error'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sandbox_sessions'
    )
    container_id = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True
    )
    container_name = models.CharField(
        max_length=100,
        unique=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='starting'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sandbox_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.container_name} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Set expiration time on creation
        if not self.pk and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(
                seconds=settings.SESSION_COOKIE_AGE
            )
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return timezone.now() > self.expires_at
    
    def extend_session(self, minutes: int = 30) -> None:
        """Extend session expiration time."""
        self.expires_at = timezone.now() + timedelta(minutes=minutes)
        self.save(update_fields=['expires_at'])
