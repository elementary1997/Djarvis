"""
Models for exercises and practical tasks.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify
import json

User = get_user_model()


class Exercise(models.Model):
    """Practical exercise/task model."""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='exercises',
        help_text='Associated lesson'
    )
    title = models.CharField(
        max_length=200,
        help_text='Exercise title'
    )
    slug = models.SlugField(
        max_length=200,
        help_text='URL-friendly identifier'
    )
    description = models.TextField(
        help_text='Exercise description and requirements in Markdown'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='easy'
    )
    order = models.IntegerField(
        default=0,
        help_text='Display order within lesson'
    )
    points = models.IntegerField(
        default=10,
        help_text='Points awarded for completion'
    )
    initial_code = models.TextField(
        blank=True,
        help_text='Starting code template for students'
    )
    solution_code = models.TextField(
        blank=True,
        help_text='Reference solution (hidden from students)'
    )
    inventory_template = models.TextField(
        blank=True,
        help_text='Ansible inventory configuration'
    )
    test_cases = models.JSONField(
        default=list,
        help_text='Test cases for validation (JSON format)'
    )
    max_attempts = models.IntegerField(
        default=0,
        help_text='Maximum attempts allowed (0 = unlimited)'
    )
    time_limit_seconds = models.IntegerField(
        default=60,
        help_text='Time limit for code execution'
    )
    is_published = models.BooleanField(
        default=False,
        help_text='Exercise visibility status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exercises'
        ordering = ['lesson', 'order']
        unique_together = ['lesson', 'slug']
        indexes = [
            models.Index(fields=['lesson', 'order']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Hint(models.Model):
    """Progressive hints for exercises."""
    
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='hints'
    )
    order = models.IntegerField(
        default=0,
        help_text='Hint reveal order (lower numbers shown first)'
    )
    content = models.TextField(
        help_text='Hint content in Markdown'
    )
    points_penalty = models.IntegerField(
        default=0,
        help_text='Points deducted when hint is revealed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hints'
        ordering = ['exercise', 'order']
        unique_together = ['exercise', 'order']
    
    def __str__(self):
        return f"Hint {self.order} for {self.exercise.title}"


class Submission(models.Model):
    """Student exercise submission."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    code = models.TextField(
        help_text='Submitted code'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    output = models.TextField(
        blank=True,
        help_text='Execution output'
    )
    error_message = models.TextField(
        blank=True,
        help_text='Error details if execution failed'
    )
    test_results = models.JSONField(
        default=dict,
        help_text='Detailed test case results'
    )
    execution_time_ms = models.IntegerField(
        default=0,
        help_text='Execution time in milliseconds'
    )
    points_earned = models.IntegerField(
        default=0,
        help_text='Points earned from this submission'
    )
    hints_used = models.JSONField(
        default=list,
        help_text='List of hint IDs revealed'
    )
    attempt_number = models.IntegerField(
        default=1,
        help_text='Attempt number for this exercise'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'submissions'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['user', 'exercise']),
            models.Index(fields=['status']),
            models.Index(fields=['-submitted_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.exercise.title} (#{self.attempt_number})"
    
    @property
    def is_successful(self):
        """Check if submission passed."""
        return self.status == 'passed'
    
    def calculate_points(self):
        """Calculate points based on hints used and penalties."""
        base_points = self.exercise.points
        hints_penalty = sum(
            Hint.objects.filter(
                id__in=self.hints_used
            ).values_list('points_penalty', flat=True)
        )
        return max(0, base_points - hints_penalty)


class HintUsage(models.Model):
    """Track hint usage by students."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='hint_usages'
    )
    hint = models.ForeignKey(
        Hint,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    revealed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hint_usages'
        unique_together = ['user', 'hint']
        ordering = ['-revealed_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.hint}"
