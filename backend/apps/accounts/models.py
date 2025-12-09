"""
User model и профили пользователей.

Архитектурное решение:
- Расширенная модель User с дополнительными полями для трекинга
- Использование AbstractUser для гибкости
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model с расширенными полями."""
    
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(_('biography'), max_length=500, blank=True)
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    
    # Statistics
    total_exercises_completed = models.IntegerField(_('total exercises completed'), default=0)
    total_points = models.IntegerField(_('total points'), default=0)
    current_streak = models.IntegerField(_('current streak days'), default=0)
    longest_streak = models.IntegerField(_('longest streak days'), default=0)
    last_activity_date = models.DateField(_('last activity date'), null=True, blank=True)
    
    # Settings
    email_notifications = models.BooleanField(_('email notifications'), default=True)
    theme = models.CharField(
        _('theme'),
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['-total_points']),
        ]
    
    def __str__(self) -> str:
        return self.email
    
    def update_streak(self) -> None:
        """Обновляет streak пользователя на основе последней активности."""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.last_activity_date:
            days_diff = (today - self.last_activity_date).days
            
            if days_diff == 1:
                # Продолжаем streak
                self.current_streak += 1
                self.longest_streak = max(self.current_streak, self.longest_streak)
            elif days_diff > 1:
                # Сбрасываем streak
                self.current_streak = 1
        else:
            self.current_streak = 1
        
        self.last_activity_date = today
        self.save(update_fields=['current_streak', 'longest_streak', 'last_activity_date'])
