"""
Serializers for exercises app.
"""
from rest_framework import serializers
from .models import Exercise, Hint, Submission, HintUsage


class HintSerializer(serializers.ModelSerializer):
    """Serializer for Hint model."""
    
    is_revealed = serializers.SerializerMethodField()
    
    class Meta:
        model = Hint
        fields = [
            'id', 'order', 'content', 'points_penalty', 'is_revealed'
        ]
    
    def get_is_revealed(self, obj):
        """Check if hint is revealed for current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return HintUsage.objects.filter(
                user=request.user,
                hint=obj
            ).exists()
        return False


class ExerciseSerializer(serializers.ModelSerializer):
    """Detailed serializer for Exercise model."""
    
    hints = HintSerializer(many=True, read_only=True)
    user_attempts = serializers.SerializerMethodField()
    best_submission = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'title', 'slug', 'description', 'difficulty',
            'points', 'initial_code', 'inventory_template',
            'max_attempts', 'time_limit_seconds', 'hints',
            'user_attempts', 'best_submission', 'is_completed',
            'created_at'
        ]
    
    def get_user_attempts(self, obj):
        """Get number of attempts by current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Submission.objects.filter(
                user=request.user,
                exercise=obj
            ).count()
        return 0
    
    def get_best_submission(self, obj):
        """Get user's best submission."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            submission = Submission.objects.filter(
                user=request.user,
                exercise=obj,
                status='passed'
            ).order_by('-points_earned').first()
            
            if submission:
                return {
                    'id': submission.id,
                    'points_earned': submission.points_earned,
                    'submitted_at': submission.submitted_at
                }
        return None
    
    def get_is_completed(self, obj):
        """Check if exercise is completed by user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Submission.objects.filter(
                user=request.user,
                exercise=obj,
                status='passed'
            ).exists()
        return False


class ExerciseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for exercise lists."""
    
    is_completed = serializers.SerializerMethodField()
    user_attempts = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'title', 'slug', 'difficulty', 'points',
            'max_attempts', 'is_completed', 'user_attempts'
        ]
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Submission.objects.filter(
                user=request.user,
                exercise=obj,
                status='passed'
            ).exists()
        return False
    
    def get_user_attempts(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Submission.objects.filter(
                user=request.user,
                exercise=obj
            ).count()
        return 0


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Submission model."""
    
    exercise_title = serializers.CharField(source='exercise.title', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'exercise', 'exercise_title', 'code', 'status',
            'output', 'error_message', 'test_results',
            'execution_time_ms', 'points_earned', 'attempt_number',
            'submitted_at'
        ]
        read_only_fields = [
            'status', 'output', 'error_message', 'test_results',
            'execution_time_ms', 'points_earned', 'attempt_number',
            'submitted_at'
        ]


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating submissions."""
    
    class Meta:
        model = Submission
        fields = ['exercise', 'code']
    
    def validate(self, attrs):
        """Validate submission."""
        exercise = attrs.get('exercise')
        user = self.context['request'].user
        
        # Check max attempts
        if exercise.max_attempts > 0:
            attempt_count = Submission.objects.filter(
                user=user,
                exercise=exercise
            ).count()
            
            if attempt_count >= exercise.max_attempts:
                raise serializers.ValidationError(
                    f"Maximum {exercise.max_attempts} attempts allowed for this exercise."
                )
        
        return attrs
    
    def create(self, validated_data):
        """Create submission with auto-increment attempt number."""
        user = self.context['request'].user
        exercise = validated_data['exercise']
        
        # Get attempt number
        last_attempt = Submission.objects.filter(
            user=user,
            exercise=exercise
        ).order_by('-attempt_number').first()
        
        attempt_number = (last_attempt.attempt_number + 1) if last_attempt else 1
        
        # Get client IP
        request = self.context['request']
        ip_address = request.META.get('REMOTE_ADDR')
        
        # Get hints used
        hints_used = list(
            HintUsage.objects.filter(
                user=user,
                hint__exercise=exercise
            ).values_list('hint_id', flat=True)
        )
        
        return Submission.objects.create(
            user=user,
            attempt_number=attempt_number,
            ip_address=ip_address,
            hints_used=hints_used,
            **validated_data
        )


class HintUsageSerializer(serializers.ModelSerializer):
    """Serializer for HintUsage model."""
    
    hint_content = serializers.CharField(source='hint.content', read_only=True)
    points_penalty = serializers.IntegerField(source='hint.points_penalty', read_only=True)
    
    class Meta:
        model = HintUsage
        fields = [
            'id', 'hint', 'hint_content', 'points_penalty', 'revealed_at'
        ]
        read_only_fields = ['revealed_at']
