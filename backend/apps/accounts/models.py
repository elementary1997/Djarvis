"""
User models for authentication and profile management.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    
    Attributes:
        email: Unique email address for authentication
        avatar: User profile picture
        bio: Short biography
        total_xp: Total experience points earned
        level: Current user level
        is_verified: Email verification status
        preferred_language: Preferred programming language
    """
    
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text='User profile picture'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text='Short biography'
    )
    total_xp = models.PositiveIntegerField(
        default=0,
        help_text='Total experience points'
    )
    level = models.PositiveIntegerField(
        default=1,
        help_text='Current user level'
    )
    is_verified = models.BooleanField(
        default=False,
        help_text='Email verification status'
    )
    preferred_language = models.CharField(
        max_length=10,
        default='python',
        help_text='Preferred programming language'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Make email the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.email} (Level {self.level})"
    
    def add_xp(self, xp: int) -> None:
        """Add experience points and level up if necessary."""
        self.total_xp += xp
        # Simple leveling: every 1000 XP = 1 level
        new_level = (self.total_xp // 1000) + 1
        if new_level > self.level:
            self.level = new_level
        self.save(update_fields=['total_xp', 'level'])
    
    @property
    def xp_to_next_level(self) -> int:
        """Calculate XP needed for next level."""
        return (self.level * 1000) - self.total_xp
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress to next level as percentage."""
        current_level_xp = (self.level - 1) * 1000
        next_level_xp = self.level * 1000
        progress_xp = self.total_xp - current_level_xp
        total_xp_needed = next_level_xp - current_level_xp
        return (progress_xp / total_xp_needed) * 100 if total_xp_needed > 0 else 0


class Achievement(models.Model):
    """
    Achievements that users can unlock.
    
    Attributes:
        name: Achievement name
        description: Achievement description
        icon: Achievement icon/badge
        xp_reward: XP points awarded
        requirement_type: Type of requirement (e.g., 'complete_lessons', 'streak')
        requirement_value: Value needed to unlock
    """
    
    REQUIREMENT_TYPES = [
        ('complete_lessons', 'Complete Lessons'),
        ('complete_exercises', 'Complete Exercises'),
        ('streak_days', 'Daily Streak'),
        ('perfect_score', 'Perfect Score'),
        ('speed_run', 'Speed Run'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏆')
    xp_reward = models.PositiveIntegerField(default=100)
    requirement_type = models.CharField(
        max_length=30,
        choices=REQUIREMENT_TYPES
    )
    requirement_value = models.PositiveIntegerField(
        help_text='Value needed to unlock achievement'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'achievements'
        verbose_name = _('Achievement')
        verbose_name_plural = _('Achievements')
        ordering = ['requirement_value']
    
    def __str__(self) -> str:
        return f"{self.icon} {self.name}"


class UserAchievement(models.Model):
    """
    Junction table tracking user achievements.
    
    Attributes:
        user: User who unlocked the achievement
        achievement: Achievement that was unlocked
        unlocked_at: Timestamp when achievement was unlocked
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='users'
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_achievements'
        verbose_name = _('User Achievement')
        verbose_name_plural = _('User Achievements')
        unique_together = ['user', 'achievement']
        ordering = ['-unlocked_at']
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.achievement.name}"
