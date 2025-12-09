"""
Models for courses, modules, and lessons.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Course(models.Model):
    """Main course model."""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text='Course title'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text='URL-friendly course identifier'
    )
    description = models.TextField(
        help_text='Detailed course description'
    )
    short_description = models.CharField(
        max_length=300,
        help_text='Brief course overview'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner'
    )
    thumbnail = models.ImageField(
        upload_to='courses/thumbnails/',
        null=True,
        blank=True
    )
    estimated_hours = models.IntegerField(
        default=0,
        help_text='Estimated completion time in hours'
    )
    is_published = models.BooleanField(
        default=False,
        help_text='Course visibility status'
    )
    order = models.IntegerField(
        default=0,
        help_text='Display order'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_courses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def total_modules(self):
        """Count of modules in course."""
        return self.modules.count()
    
    @property
    def total_lessons(self):
        """Count of lessons in course."""
        return sum(module.lessons.count() for module in self.modules.all())


class Module(models.Model):
    """Course module/chapter."""
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    title = models.CharField(
        max_length=200,
        help_text='Module title'
    )
    slug = models.SlugField(
        max_length=200,
        help_text='URL-friendly module identifier'
    )
    description = models.TextField(
        blank=True,
        help_text='Module description'
    )
    order = models.IntegerField(
        default=0,
        help_text='Display order within course'
    )
    is_published = models.BooleanField(
        default=False,
        help_text='Module visibility status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'modules'
        ordering = ['course', 'order']
        unique_together = ['course', 'slug']
        indexes = [
            models.Index(fields=['course', 'order']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def total_lessons(self):
        """Count of lessons in module."""
        return self.lessons.count()


class Lesson(models.Model):
    """Individual lesson within a module."""
    
    LESSON_TYPE_CHOICES = [
        ('theory', 'Theory'),
        ('practice', 'Practice'),
        ('quiz', 'Quiz'),
        ('project', 'Project'),
    ]
    
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(
        max_length=200,
        help_text='Lesson title'
    )
    slug = models.SlugField(
        max_length=200,
        help_text='URL-friendly lesson identifier'
    )
    lesson_type = models.CharField(
        max_length=20,
        choices=LESSON_TYPE_CHOICES,
        default='theory'
    )
    content = models.TextField(
        help_text='Lesson content in Markdown format'
    )
    order = models.IntegerField(
        default=0,
        help_text='Display order within module'
    )
    estimated_minutes = models.IntegerField(
        default=10,
        help_text='Estimated completion time in minutes'
    )
    is_published = models.BooleanField(
        default=False,
        help_text='Lesson visibility status'
    )
    video_url = models.URLField(
        blank=True,
        help_text='Optional video tutorial URL'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        ordering = ['module', 'order']
        unique_together = ['module', 'slug']
        indexes = [
            models.Index(fields=['module', 'order']),
        ]
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class CourseEnrollment(models.Model):
    """Track user enrollments in courses."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Course completion timestamp'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Enrollment active status'
    )
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Course completion percentage'
    )
    
    class Meta:
        db_table = 'course_enrollments'
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
    
    @property
    def is_completed(self):
        """Check if course is completed."""
        return self.completed_at is not None


class LessonCompletion(models.Model):
    """Track user lesson completions."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lesson_completions'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='completions'
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    time_spent_minutes = models.IntegerField(
        default=0,
        help_text='Time spent on lesson in minutes'
    )
    
    class Meta:
        db_table = 'lesson_completions'
        unique_together = ['user', 'lesson']
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['user', 'completed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.lesson.title}"
