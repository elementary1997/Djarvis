"""
Models for course modules and lessons.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Module(models.Model):
    """
    Learning module (e.g., "Basic Ansible", "Advanced Playbooks").
    
    Attributes:
        title: Module title
        description: Module description
        difficulty: Difficulty level (beginner, intermediate, advanced)
        order: Display order
        icon: Module icon emoji
        estimated_hours: Estimated completion time
        is_published: Publication status
    """
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    icon = models.CharField(
        max_length=50,
        default='📚',
        help_text='Module icon emoji'
    )
    estimated_hours = models.PositiveIntegerField(
        default=5,
        help_text='Estimated completion time in hours'
    )
    is_published = models.BooleanField(
        default=False,
        help_text='Whether module is visible to students'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'modules'
        verbose_name = _('Module')
        verbose_name_plural = _('Modules')
        ordering = ['order', 'title']
    
    def __str__(self) -> str:
        return f"{self.icon} {self.title} ({self.get_difficulty_display()})"
    
    @property
    def total_lessons(self) -> int:
        """Count total lessons in module."""
        return self.lessons.count()
    
    @property
    def total_exercises(self) -> int:
        """Count total exercises in module."""
        return sum(lesson.exercises.count() for lesson in self.lessons.all())


class Lesson(models.Model):
    """
    Individual lesson within a module.
    
    Attributes:
        module: Parent module
        title: Lesson title
        content: Markdown content for theory
        order: Display order within module
        xp_reward: XP points for completing lesson
        estimated_minutes: Estimated time to complete
        is_published: Publication status
    """
    
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    content = models.TextField(
        help_text='Markdown formatted lesson content'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order within module'
    )
    xp_reward = models.PositiveIntegerField(
        default=50,
        help_text='XP points awarded for completion'
    )
    estimated_minutes = models.PositiveIntegerField(
        default=15,
        help_text='Estimated time to complete in minutes'
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ['module', 'order', 'title']
        unique_together = ['module', 'slug']
    
    def __str__(self) -> str:
        return f"{self.module.title} - {self.title}"
    
    @property
    def exercise_count(self) -> int:
        """Count exercises in this lesson."""
        return self.exercises.count()


class LessonResource(models.Model):
    """
    Additional resources attached to lessons.
    
    Attributes:
        lesson: Parent lesson
        title: Resource title
        resource_type: Type of resource (link, file, video)
        url: External URL or file path
        description: Resource description
    """
    
    RESOURCE_TYPES = [
        ('link', 'External Link'),
        ('file', 'Downloadable File'),
        ('video', 'Video'),
        ('documentation', 'Documentation'),
    ]
    
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    title = models.CharField(max_length=200)
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPES
    )
    url = models.URLField(max_length=500)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'lesson_resources'
        verbose_name = _('Lesson Resource')
        verbose_name_plural = _('Lesson Resources')
        ordering = ['lesson', 'order', 'title']
    
    def __str__(self) -> str:
        return f"{self.lesson.title} - {self.title}"
