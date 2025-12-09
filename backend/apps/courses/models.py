"""
Модели для курсов, модулей и уроков.

Архитектурное решение:
- Иерархическая структура: Course -> Module -> Lesson
- Markdown для контента с поддержкой интерактивных элементов
- Порядок через ordering поля для гибкой сортировки
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from markdownx.models import MarkdownxField


class DifficultyLevel(models.TextChoices):
    """Уровни сложности курсов/модулей."""
    BEGINNER = 'beginner', _('Beginner')
    INTERMEDIATE = 'intermediate', _('Intermediate')
    ADVANCED = 'advanced', _('Advanced')


class Course(models.Model):
    """Курс - верхний уровень структуры обучения."""
    
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique=True, max_length=200)
    description = models.TextField(_('description'))
    cover_image = models.ImageField(
        _('cover image'),
        upload_to='courses/covers/',
        blank=True,
        null=True
    )
    difficulty = models.CharField(
        _('difficulty'),
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER
    )
    estimated_hours = models.PositiveIntegerField(
        _('estimated hours'),
        validators=[MinValueValidator(1)],
        help_text=_('Estimated time to complete in hours')
    )
    ordering = models.IntegerField(_('ordering'), default=0)
    is_published = models.BooleanField(_('is published'), default=False)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('course')
        verbose_name_plural = _('courses')
        ordering = ['ordering', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_published', 'ordering']),
        ]
    
    def __str__(self) -> str:
        return self.title
    
    @property
    def total_modules(self) -> int:
        """Возвращает количество модулей в курсе."""
        return self.modules.count()
    
    @property
    def total_lessons(self) -> int:
        """Возвращает общее количество уроков во всех модулях."""
        return sum(module.lessons.count() for module in self.modules.all())


class Module(models.Model):
    """Модуль - раздел курса, содержащий уроки."""
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name=_('course')
    )
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200)
    description = models.TextField(_('description'))
    difficulty = models.CharField(
        _('difficulty'),
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER
    )
    ordering = models.IntegerField(_('ordering'), default=0)
    is_published = models.BooleanField(_('is published'), default=False)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('module')
        verbose_name_plural = _('modules')
        ordering = ['ordering', 'title']
        unique_together = [['course', 'slug']]
        indexes = [
            models.Index(fields=['course', 'ordering']),
        ]
    
    def __str__(self) -> str:
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """Урок - отдельная единица контента с теорией."""
    
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('module')
    )
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200)
    content = MarkdownxField(_('content'), help_text=_('Markdown formatted content'))
    
    # Video content (optional)
    video_url = models.URLField(_('video URL'), blank=True, null=True)
    
    estimated_minutes = models.PositiveIntegerField(
        _('estimated minutes'),
        validators=[MinValueValidator(1)],
        help_text=_('Estimated time to complete in minutes')
    )
    ordering = models.IntegerField(_('ordering'), default=0)
    is_published = models.BooleanField(_('is published'), default=False)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')
        ordering = ['ordering', 'title']
        unique_together = [['module', 'slug']]
        indexes = [
            models.Index(fields=['module', 'ordering']),
        ]
    
    def __str__(self) -> str:
        return f"{self.module.title} - {self.title}"
