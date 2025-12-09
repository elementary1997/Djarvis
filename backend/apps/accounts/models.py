"""
User models for authentication and profiles.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model with additional fields."""
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Administrator'),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        help_text='User role in the platform'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text='User profile picture'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text='User biography'
    )
    github_username = models.CharField(
        max_length=100,
        blank=True,
        help_text='GitHub username for integration'
    )
    is_email_verified = models.BooleanField(
        default=False,
        help_text='Email verification status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Required for email as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def full_name(self):
        """Return user's full name."""
        return self.get_full_name() or self.username
    
    def is_student(self):
        """Check if user is a student."""
        return self.role == 'student'
    
    def is_instructor(self):
        """Check if user is an instructor."""
        return self.role == 'instructor'
    
    def is_administrator(self):
        """Check if user is an administrator."""
        return self.role == 'admin' or self.is_superuser


class UserProfile(models.Model):
    """Extended user profile information."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text='User timezone'
    )
    language = models.CharField(
        max_length=10,
        default='en',
        help_text='Preferred language'
    )
    notifications_enabled = models.BooleanField(
        default=True,
        help_text='Enable email notifications'
    )
    receive_marketing_emails = models.BooleanField(
        default=False,
        help_text='Receive marketing communications'
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='Last login IP address'
    )
    total_points = models.IntegerField(
        default=0,
        help_text='Total points earned'
    )
    streak_days = models.IntegerField(
        default=0,
        help_text='Consecutive days of activity'
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text='Last activity timestamp'
    )
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile of {self.user.email}"
