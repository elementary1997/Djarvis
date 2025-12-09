"""
Модели для практических заданий и подсказок.

Архитектурное решение:
- Гибкая система тестов через JSON поле
- Progressive hints система (от общих к конкретным)
- Баллы и веремя для gamification
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from markdownx.models import MarkdownxField


class Exercise(models.Model):
    """Практическое задание для студентов."""
    
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='exercises',
        verbose_name=_('lesson')
    )
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200)
    description = MarkdownxField(
        _('description'),
        help_text=_('Exercise description and requirements')
    )
    
    # Initial code template
    starter_code = models.TextField(
        _('starter code'),
        blank=True,
        help_text=_('Initial Ansible code template for students')
    )
    
    # Solution (for reference)
    solution_code = models.TextField(
        _('solution code'),
        help_text=_('Reference solution (not shown to students)')
    )
    
    # Test configuration (JSON format)
    # Example: [{"type": "file_exists", "path": "/etc/nginx/nginx.conf"}, ...]
    tests = models.JSONField(
        _('tests'),
        default=list,
        help_text=_('Test cases to validate student solution')
    )
    
    points = models.PositiveIntegerField(
        _('points'),
        default=10,
        validators=[MinValueValidator(1)]
    )
    time_limit_seconds = models.PositiveIntegerField(
        _('time limit (seconds)'),
        default=300,
        validators=[MinValueValidator(10)]
    )
    ordering = models.IntegerField(_('ordering'), default=0)
    is_published = models.BooleanField(_('is published'), default=False)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('exercise')
        verbose_name_plural = _('exercises')
        ordering = ['ordering', 'title']
        unique_together = [['lesson', 'slug']]
        indexes = [
            models.Index(fields=['lesson', 'ordering']),
        ]
    
    def __str__(self) -> str:
        return f"{self.lesson.title} - {self.title}"


class Hint(models.Model):
    """Подсказки для заданий (прогрессивные)."""
    
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='hints',
        verbose_name=_('exercise')
    )
    content = models.TextField(_('content'), help_text=_('Hint text'))
    ordering = models.IntegerField(
        _('ordering'),
        default=0,
        help_text=_('Order of hints (from general to specific)')
    )
    penalty_points = models.PositiveIntegerField(
        _('penalty points'),
        default=1,
        help_text=_('Points deducted when hint is revealed')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('hint')
        verbose_name_plural = _('hints')
        ordering = ['ordering']
        indexes = [
            models.Index(fields=['exercise', 'ordering']),
        ]
    
    def __str__(self) -> str:
        return f"{self.exercise.title} - Hint #{self.ordering}"
