"""
Models for tracking user progress.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.courses.models import Module, Lesson


class ModuleProgress(models.Model):
    """
    Track user progress through modules.
    
    Attributes:
        user: Student
        module: Module being tracked
        is_started: Whether module has been started
        is_completed: Whether module is completed
        completion_percentage: Percentage of lessons completed
        started_at: When module was first accessed
        completed_at: When module was completed
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='module_progress'
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    is_started = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.FloatField(default=0.0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'module_progress'
        unique_together = ['user', 'module']
        ordering = ['-started_at']
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.module.title} ({self.completion_percentage:.1f}%)"
    
    def update_progress(self) -> None:
        """Recalculate completion percentage."""
        total_lessons = self.module.lessons.filter(is_published=True).count()
        if total_lessons == 0:
            self.completion_percentage = 0.0
            return
        
        completed_lessons = LessonProgress.objects.filter(
            user=self.user,
            lesson__module=self.module,
            is_completed=True
        ).count()
        
        self.completion_percentage = (completed_lessons / total_lessons) * 100
        
        if self.completion_percentage >= 100 and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
        
        self.save(update_fields=['completion_percentage', 'is_completed', 'completed_at'])


class LessonProgress(models.Model):
    """
    Track user progress through lessons.
    
    Attributes:
        user: Student
        lesson: Lesson being tracked
        is_completed: Whether lesson is completed
        time_spent: Total time spent on lesson (seconds)
        last_accessed: Last time lesson was accessed
        completed_at: When lesson was completed
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    is_completed = models.BooleanField(default=False)
    time_spent = models.PositiveIntegerField(
        default=0,
        help_text='Time spent in seconds'
    )
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'lesson_progress'
        unique_together = ['user', 'lesson']
        ordering = ['-last_accessed']
    
    def __str__(self) -> str:
        status = "✅" if self.is_completed else "🟡"
        return f"{status} {self.user.email} - {self.lesson.title}"
    
    def mark_completed(self) -> None:
        """Mark lesson as completed and award XP."""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save(update_fields=['is_completed', 'completed_at'])
            
            # Award XP
            self.user.add_xp(self.lesson.xp_reward)
            
            # Update module progress
            module_progress, created = ModuleProgress.objects.get_or_create(
                user=self.user,
                module=self.lesson.module,
                defaults={'is_started': True, 'started_at': timezone.now()}
            )
            module_progress.update_progress()


class DailyStreak(models.Model):
    """
    Track user's daily activity streaks.
    
    Attributes:
        user: Student
        current_streak: Current consecutive days
        longest_streak: Longest streak achieved
        last_activity_date: Last day user was active
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_streak'
    )
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'daily_streaks'
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.current_streak} days streak"
    
    def update_streak(self) -> None:
        """Update streak based on activity."""
        today = timezone.now().date()
        
        if not self.last_activity_date:
            # First activity
            self.current_streak = 1
            self.longest_streak = 1
            self.last_activity_date = today
        elif self.last_activity_date == today:
            # Already counted today
            return
        elif self.last_activity_date == today - timedelta(days=1):
            # Consecutive day
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
            self.last_activity_date = today
        else:
            # Streak broken
            self.current_streak = 1
            self.last_activity_date = today
        
        self.save()
