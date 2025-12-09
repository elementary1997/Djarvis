"""
Модели для трекинга прогресса пользователей.

Архитектурное решение:
- Детальный трекинг по курсам, модулям, урокам и заданиям
- Система достижений для gamification
- Статистика использования подсказок
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class LessonProgress(models.Model):
    """Прогресс пользователя по уроку."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name=_('user')
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name=_('lesson')
    )
    
    is_completed = models.BooleanField(_('is completed'), default=False)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('lesson progress')
        verbose_name_plural = _('lesson progress')
        unique_together = [['user', 'lesson']]
        indexes = [
            models.Index(fields=['user', 'is_completed']),
        ]
    
    def __str__(self) -> str:
        status = 'Completed' if self.is_completed else 'In Progress'
        return f"{self.user.email} - {self.lesson.title} ({status})"


class ExerciseProgress(models.Model):
    """Прогресс пользователя по заданию."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exercise_progress',
        verbose_name=_('user')
    )
    exercise = models.ForeignKey(
        'exercises.Exercise',
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name=_('exercise')
    )
    
    is_completed = models.BooleanField(_('is completed'), default=False)
    attempts = models.PositiveIntegerField(_('attempts'), default=0)
    hints_used = models.PositiveIntegerField(_('hints used'), default=0)
    points_earned = models.PositiveIntegerField(_('points earned'), default=0)
    best_execution_time = models.FloatField(
        _('best execution time'),
        null=True,
        blank=True
    )
    
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('exercise progress')
        verbose_name_plural = _('exercise progress')
        unique_together = [['user', 'exercise']]
        indexes = [
            models.Index(fields=['user', 'is_completed']),
        ]
    
    def __str__(self) -> str:
        status = 'Completed' if self.is_completed else f'{self.attempts} attempts'
        return f"{self.user.email} - {self.exercise.title} ({status})"


class Achievement(models.Model):
    """Достижения для gamification."""
    
    title = models.CharField(_('title'), max_length=100)
    description = models.TextField(_('description'))
    icon = models.CharField(
        _('icon'),
        max_length=50,
        help_text=_('Icon name or emoji')
    )
    
    # Criteria (JSON format)
    criteria = models.JSONField(
        _('criteria'),
        help_text=_('Achievement unlock criteria')
    )
    
    points = models.PositiveIntegerField(_('points'), default=0)
    is_active = models.BooleanField(_('is active'), default=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('achievement')
        verbose_name_plural = _('achievements')
        ordering = ['-points', 'title']
    
    def __str__(self) -> str:
        return self.title


class UserAchievement(models.Model):
    """Связь пользователей с их достижениями."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name=_('user')
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name=_('achievement')
    )
    
    unlocked_at = models.DateTimeField(_('unlocked at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('user achievement')
        verbose_name_plural = _('user achievements')
        unique_together = [['user', 'achievement']]
        ordering = ['-unlocked_at']
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.achievement.title}"
