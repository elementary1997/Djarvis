"""
Модели для трекинга выполнения кода в sandbox.

Архитектурное решение:
- Логирование всех попыток выполнения
- Сохранение stdout/stderr для анализа
- Celery tasks для асинхронного выполнения
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class ExecutionStatus(models.TextChoices):
    """Статусы выполнения."""
    PENDING = 'pending', _('Pending')
    RUNNING = 'running', _('Running')
    SUCCESS = 'success', _('Success')
    FAILED = 'failed', _('Failed')
    TIMEOUT = 'timeout', _('Timeout')
    ERROR = 'error', _('Error')


class Execution(models.Model):
    """Запись о выполнении кода в sandbox."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name=_('user')
    )
    exercise = models.ForeignKey(
        'exercises.Exercise',
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name=_('exercise')
    )
    
    code = models.TextField(_('code'), help_text=_('Submitted Ansible code'))
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PENDING
    )
    
    # Results
    stdout = models.TextField(_('stdout'), blank=True)
    stderr = models.TextField(_('stderr'), blank=True)
    test_results = models.JSONField(_('test results'), default=dict)
    passed = models.BooleanField(_('passed'), default=False)
    
    # Metrics
    execution_time_seconds = models.FloatField(
        _('execution time (seconds)'),
        null=True,
        blank=True
    )
    points_earned = models.PositiveIntegerField(_('points earned'), default=0)
    
    # Container info
    container_id = models.CharField(
        _('container ID'),
        max_length=100,
        blank=True
    )
    
    # Celery task
    celery_task_id = models.CharField(
        _('celery task ID'),
        max_length=100,
        blank=True
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('execution')
        verbose_name_plural = _('executions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['exercise', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.exercise.title} ({self.status})"
