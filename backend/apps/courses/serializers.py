"""
Serializers for courses app.
"""
from rest_framework import serializers
from .models import (
    Course, Module, Lesson,
    CourseEnrollment, LessonCompletion
)


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model."""
    
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'lesson_type', 'content',
            'order', 'estimated_minutes', 'video_url',
            'is_completed', 'created_at'
        ]
    
    def get_is_completed(self, obj):
        """Check if lesson is completed by current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LessonCompletion.objects.filter(
                user=request.user,
                lesson=obj
            ).exists()
        return False


class LessonListSerializer(serializers.ModelSerializer):
    """Simplified serializer for lesson lists."""
    
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'lesson_type',
            'order', 'estimated_minutes', 'is_completed'
        ]
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LessonCompletion.objects.filter(
                user=request.user,
                lesson=obj
            ).exists()
        return False


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for Module model."""
    
    lessons = LessonListSerializer(many=True, read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'slug', 'description',
            'order', 'total_lessons', 'lessons', 'created_at'
        ]


class ModuleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for module lists."""
    
    total_lessons = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'slug', 'description',
            'order', 'total_lessons'
        ]


class CourseSerializer(serializers.ModelSerializer):
    """Detailed serializer for Course model."""
    
    modules = ModuleSerializer(many=True, read_only=True)
    total_modules = serializers.IntegerField(read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'difficulty', 'thumbnail', 'estimated_hours',
            'total_modules', 'total_lessons', 'is_enrolled',
            'progress_percentage', 'modules', 'created_at'
        ]
    
    def get_is_enrolled(self, obj):
        """Check if user is enrolled in course."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CourseEnrollment.objects.filter(
                user=request.user,
                course=obj,
                is_active=True
            ).exists()
        return False
    
    def get_progress_percentage(self, obj):
        """Get user's progress in course."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            enrollment = CourseEnrollment.objects.filter(
                user=request.user,
                course=obj,
                is_active=True
            ).first()
            return enrollment.progress_percentage if enrollment else 0
        return 0


class CourseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for course lists."""
    
    total_modules = serializers.IntegerField(read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description',
            'difficulty', 'thumbnail', 'estimated_hours',
            'total_modules', 'total_lessons', 'is_enrolled'
        ]
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CourseEnrollment.objects.filter(
                user=request.user,
                course=obj,
                is_active=True
            ).exists()
        return False


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for CourseEnrollment model."""
    
    course = CourseListSerializer(read_only=True)
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'course', 'enrolled_at', 'completed_at',
            'is_active', 'progress_percentage', 'is_completed'
        ]
        read_only_fields = ['enrolled_at', 'completed_at', 'progress_percentage']


class LessonCompletionSerializer(serializers.ModelSerializer):
    """Serializer for LessonCompletion model."""
    
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = LessonCompletion
        fields = [
            'id', 'lesson', 'lesson_title',
            'completed_at', 'time_spent_minutes'
        ]
        read_only_fields = ['completed_at']
