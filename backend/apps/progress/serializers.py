"""
Serializers for progress tracking.
"""
from rest_framework import serializers
from .models import ModuleProgress, LessonProgress, DailyStreak
from apps.courses.serializers import ModuleListSerializer, LessonListSerializer


class ModuleProgressSerializer(serializers.ModelSerializer):
    """Serializer for module progress."""
    
    module = ModuleListSerializer(read_only=True)
    
    class Meta:
        model = ModuleProgress
        fields = [
            'id', 'module', 'is_started', 'is_completed',
            'completion_percentage', 'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'completion_percentage']


class LessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for lesson progress."""
    
    lesson = LessonListSerializer(read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson', 'is_completed', 'time_spent',
            'last_accessed', 'completed_at'
        ]
        read_only_fields = ['id', 'last_accessed']


class DailyStreakSerializer(serializers.ModelSerializer):
    """Serializer for daily streak."""
    
    class Meta:
        model = DailyStreak
        fields = [
            'id', 'current_streak', 'longest_streak', 'last_activity_date'
        ]
        read_only_fields = ['id']


class MarkLessonCompleteSerializer(serializers.Serializer):
    """Serializer for marking lesson as complete."""
    
    lesson_id = serializers.IntegerField(required=True)
    time_spent = serializers.IntegerField(
        required=False,
        min_value=0,
        help_text='Time spent in seconds'
    )
