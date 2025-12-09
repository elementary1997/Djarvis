"""
Serializers for courses and lessons.
"""
from rest_framework import serializers
from .models import Module, Lesson, LessonResource


class LessonResourceSerializer(serializers.ModelSerializer):
    """Serializer for lesson resources."""
    
    class Meta:
        model = LessonResource
        fields = [
            'id', 'title', 'resource_type', 'url',
            'description', 'order'
        ]


class LessonListSerializer(serializers.ModelSerializer):
    """Serializer for lesson list view."""
    
    exercise_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'order', 'xp_reward',
            'estimated_minutes', 'exercise_count', 'is_published'
        ]


class LessonDetailSerializer(serializers.ModelSerializer):
    """Serializer for lesson detail view."""
    
    exercise_count = serializers.IntegerField(read_only=True)
    resources = LessonResourceSerializer(many=True, read_only=True)
    module_title = serializers.CharField(source='module.title', read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'module', 'module_title', 'title', 'slug',
            'content', 'order', 'xp_reward', 'estimated_minutes',
            'exercise_count', 'resources', 'is_published',
            'created_at', 'updated_at'
        ]


class ModuleListSerializer(serializers.ModelSerializer):
    """Serializer for module list view."""
    
    total_lessons = serializers.IntegerField(read_only=True)
    total_exercises = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'slug', 'description', 'difficulty',
            'icon', 'order', 'estimated_hours', 'total_lessons',
            'total_exercises', 'is_published'
        ]


class ModuleDetailSerializer(serializers.ModelSerializer):
    """Serializer for module detail view."""
    
    lessons = LessonListSerializer(many=True, read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    total_exercises = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'slug', 'description', 'difficulty',
            'icon', 'order', 'estimated_hours', 'total_lessons',
            'total_exercises', 'lessons', 'is_published',
            'created_at', 'updated_at'
        ]
