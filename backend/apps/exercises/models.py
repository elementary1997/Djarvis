"""
Models for exercises and student attempts.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.courses.models import Lesson
import json


class Exercise(models.Model):
    """
    Practical exercise for students.
    
    Attributes:
        lesson: Parent lesson
        title: Exercise title
        description: Task description
        instructions: Step-by-step instructions
        starter_code: Initial code template
        solution_code: Reference solution (hidden from students)
        test_cases: JSON array of test cases
        hints: JSON array of progressive hints
        xp_reward: XP points for completion
        difficulty: Exercise difficulty
        order: Display order within lesson
    """
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='exercises'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(help_text='Task description in Markdown')
    instructions = models.TextField(help_text='Step-by-step instructions')
    
    # Code fields
    starter_code = models.TextField(
        blank=True,
        help_text='Initial Ansible playbook/code template'
    )
    solution_code = models.TextField(
        help_text='Reference solution (hidden from students)'
    )
    
    # Test configuration
    test_cases = models.JSONField(
        default=list,
        help_text='Array of test case definitions'
    )
    hints = models.JSONField(
        default=list,
        help_text='Progressive hints for students'
    )
    
    # Metadata
    xp_reward = models.PositiveIntegerField(default=100)
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='easy'
    )
    order = models.PositiveIntegerField(default=0)
    time_limit_seconds = models.PositiveIntegerField(
        default=300,
        help_text='Maximum execution time in seconds'
    )
    max_attempts = models.PositiveIntegerField(
        default=10,
        help_text='Maximum number of attempts (0 = unlimited)'
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exercises'
        verbose_name = _('Exercise')
        verbose_name_plural = _('Exercises')
        ordering = ['lesson', 'order', 'title']
        unique_together = ['lesson', 'slug']
    
    def __str__(self) -> str:
        return f"{self.lesson.title} - {self.title}"
    
    @property
    def completion_rate(self) -> float:
        """Calculate percentage of users who completed this exercise."""
        total_attempts = self.attempts.values('user').distinct().count()
        if total_attempts == 0:
            return 0.0
        passed_attempts = self.attempts.filter(is_passed=True).values('user').distinct().count()
        return (passed_attempts / total_attempts) * 100


class ExerciseAttempt(models.Model):
    """
    Student attempt at an exercise.
    
    Attributes:
        exercise: Exercise being attempted
        user: Student making the attempt
        code_submitted: Code submitted by student
        output: Execution output
        error_message: Error message if execution failed
        test_results: JSON object with test results
        is_passed: Whether all tests passed
        execution_time: How long execution took
        hints_used: Number of hints viewed
        attempt_number: Sequential attempt number for this user/exercise
    """
    
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exercise_attempts'
    )
    code_submitted = models.TextField()
    output = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    test_results = models.JSONField(
        default=dict,
        help_text='Detailed test execution results'
    )
    is_passed = models.BooleanField(default=False)
    execution_time = models.FloatField(
        null=True,
        help_text='Execution time in seconds'
    )
    hints_used = models.PositiveIntegerField(default=0)
    attempt_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exercise_attempts'
        verbose_name = _('Exercise Attempt')
        verbose_name_plural = _('Exercise Attempts')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'exercise', '-created_at']),
            models.Index(fields=['exercise', 'is_passed']),
        ]
    
    def __str__(self) -> str:
        status = "✅ Passed" if self.is_passed else "❌ Failed"
        return f"{self.user.email} - {self.exercise.title} - {status}"
    
    def save(self, *args, **kwargs):
        # Auto-increment attempt number
        if not self.pk:
            last_attempt = ExerciseAttempt.objects.filter(
                user=self.user,
                exercise=self.exercise
            ).order_by('-attempt_number').first()
            
            self.attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1
        
        super().save(*args, **kwargs)
