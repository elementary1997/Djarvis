"""
Serializers for exercises.
"""
from rest_framework import serializers
from .models import Exercise, ExerciseAttempt


class ExerciseListSerializer(serializers.ModelSerializer):
    """Serializer for exercise list."""
    
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    completion_rate = serializers.FloatField(read_only=True)
    user_attempts = serializers.SerializerMethodField()
    user_passed = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'lesson', 'lesson_title', 'title', 'slug',
            'description', 'difficulty', 'xp_reward', 'order',
            'max_attempts', 'time_limit_seconds', 'completion_rate',
            'user_attempts', 'user_passed'
        ]
    
    def get_user_attempts(self, obj):
        """Get number of attempts by current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.attempts.filter(user=request.user).count()
        return 0
    
    def get_user_passed(self, obj):
        """Check if user has passed this exercise."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.attempts.filter(user=request.user, is_passed=True).exists()
        return False


class ExerciseDetailSerializer(serializers.ModelSerializer):
    """Serializer for exercise detail."""
    
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    hints = serializers.JSONField(read_only=True)
    user_attempts = serializers.SerializerMethodField()
    user_best_attempt = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'lesson', 'lesson_title', 'title', 'slug',
            'description', 'instructions', 'starter_code',
            'hints', 'difficulty', 'xp_reward', 'order',
            'max_attempts', 'time_limit_seconds',
            'user_attempts', 'user_best_attempt', 'is_published'
        ]
    
    def get_user_attempts(self, obj):
        """Get user's attempts count."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.attempts.filter(user=request.user).count()
        return 0
    
    def get_user_best_attempt(self, obj):
        """Get user's best attempt."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            best = obj.attempts.filter(
                user=request.user,
                is_passed=True
            ).order_by('execution_time').first()
            if best:
                return ExerciseAttemptSerializer(best).data
        return None


class ExerciseAttemptSerializer(serializers.ModelSerializer):
    """Serializer for exercise attempts."""
    
    exercise_title = serializers.CharField(source='exercise.title', read_only=True)
    
    class Meta:
        model = ExerciseAttempt
        fields = [
            'id', 'exercise', 'exercise_title', 'code_submitted',
            'output', 'error_message', 'test_results', 'is_passed',
            'execution_time', 'hints_used', 'attempt_number', 'created_at'
        ]
        read_only_fields = ['id', 'is_passed', 'test_results', 'created_at']


class HintRequestSerializer(serializers.Serializer):
    """Serializer for hint requests."""
    
    hint_index = serializers.IntegerField(
        min_value=0,
        help_text='Index of the hint to retrieve'
    )
